from _thread import allocate_lock, start_new_thread
from binascii import hexlify
from errno import EAGAIN, ECONNRESET
from socket import getaddrinfo, socket, AF_INET, SOCK_STREAM

from utime import sleep_ms, time

from typing import Optional, Tuple, List, Union
from .constants import (
    PROTOCOL,
    TYPE_CONNECT,
    TYPE_CONNACK,
    TYPE_PUBLISH,
    TYPE_PUBACK,
    TYPE_PUBREC,
    TYPE_PUBREL,
    TYPE_PUBCOMP,
    TYPE_SUBSCRIBE,
    TYPE_SUBACK,
    TYPE_UNSUBSCRIBE,
    TYPE_UNSUBACK,
    TYPE_PINGREQ,
    TYPE_PINGRESP,
    TYPE_DISCONNECT,
)
from .types import (
    MQTTHeaderLayout,
    MQTTConnectFlagsLayout,
    MQTTConnAckLayout,
    MQTTAckRecvLayout,
    MQTTAckSendLayout,
    PubAckWaitListType,
    SubAckWaitListType,
    UnSubAckWaitListType, InboundWaitListType,
)
from .utils import (
    new_struct,
    recv_struct,
    encode_varlen_int,
    recv_varlen_int,
    encode_int,
    decode_int,
    encode_str,
    decode_str,
)


class MQTTClient:
    def __init__(
            self,
            server: str,
            client_id: str,
            lwt: Tuple[str, str, int, bool] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            keepalive=0,
            start=True,
    ):
        self.server = server
        self.client_id = client_id
        self.clean_session = True
        self.lwt = lwt
        self.username = username
        self.password = password
        self.keepalive = keepalive

        self.sock: Optional[socket] = None
        self.sock_lock = allocate_lock()

        self.connected = False
        self.last_activity = time()
        self.packet_id = 0
        self.retry_interval = 500

        self.puback_wait: PubAckWaitListType = []
        self.pubrec_wait: PubAckWaitListType = []
        self.pubcomp_wait: PubAckWaitListType = []
        self.suback_wait: SubAckWaitListType = []
        self.unsuback_wait: UnSubAckWaitListType = []

        self.inbound_wait: InboundWaitListType = []
        self.ping_wait = 0

        self.callbacks = {}

        self.run_lock = allocate_lock()
        self.should_run = False

        if start:
            self.start()

    def get_packet_id(self):
        self.packet_id += 1
        if self.packet_id > 65536:
            self.packet_id = 1
        return self.packet_id

    def get_sock(self):
        if self.sock is None:
            self.connected = False
            address = getaddrinfo(self.server, 1883)[0][-1]
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(address)
            self.sock.setblocking(False)
        return self.sock

    def wait_retry(self):
        print(f"mqtt.wait_retry: Retrying after {self.retry_interval} ms...")
        sleep_ms(self.retry_interval)
        if self.retry_interval < 4000:
            self.retry_interval *= 2

    def connect(self):
        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = TYPE_CONNECT

        flags, flags_data = new_struct(MQTTConnectFlagsLayout)
        flags.clean_session = self.clean_session

        parts = [
            PROTOCOL,
            flags_data,
            encode_int(self.keepalive),
            encode_str(self.client_id),
        ]

        if self.lwt is not None:
            parts.extend(map(encode_str, self.lwt[:2]))
            flags.will = 1
            flags.will_qos = self.lwt[2]
            flags.will_retain = self.lwt[3]

        if self.username is not None:
            parts.append(encode_str(self.username))
            flags.username = 1

        if self.password is not None:
            parts.append(encode_str(self.password))
            flags.password = 1

        data = b"".join(parts)
        data_len = encode_varlen_int(len(data))
        with self.sock_lock:
            self.get_sock().send(header_data + data_len + data)
        self.last_activity = time()

    def publish(self, topic: str, message: str, qos=0, retain=False):
        while not self.connected:
            sleep_ms(1)

        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = TYPE_PUBLISH
        header.qos = qos
        header.retain = retain

        data = encode_str(topic)
        if qos > 0:
            packet_id = self.get_packet_id()
            data += encode_int(packet_id)
            pub_wait = self.puback_wait if qos == 1 else self.pubrec_wait
            pub_wait.append((packet_id, time(), topic, message, qos, retain))
        data += message

        data_len = encode_varlen_int(len(data))
        with self.sock_lock:
            self.get_sock().send(header_data + data_len + data)
        self.last_activity = time()

    def send_puback(self, packet_id, ack_type):
        puback, puback_data = new_struct(MQTTAckSendLayout)
        puback.header.type = ack_type
        if ack_type == TYPE_PUBREL:
            puback.header.qos = 1
        puback.length = 2
        puback.packet_id = packet_id
        with self.sock_lock:
            self.get_sock().send(puback_data)
        self.last_activity = time()

        if ack_type == TYPE_PUBACK or ack_type == TYPE_PUBCOMP:
            try:
                packet_idx = [i[0] for i in self.inbound_wait].index(packet_id)
            except ValueError:
                print(f"mqtt.send_puback: WARNING just acked an unknown packet!")
                return

            packet_id, packet_time, topic, data, retained = self.inbound_wait.pop(packet_idx)

            try:
                topic = topic.decode()
            except UnicodeError:
                print(f"mqtt.send_puback: UnicodeError when trying to decode topic")
                print(f"mqtt.send_puback: DEBUG {topic}")

            cb = self.callbacks.get(topic, self.default_callback)
            cb(self, topic, data, retained)

    def send_subscribe(self, topics: Union[List[str, int], List[str]], sub_type):
        while not self.connected:
            sleep_ms(1)

        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = sub_type
        header.qos = 1

        packet_id = self.get_packet_id()
        parts = [encode_int(packet_id)]

        if sub_type == TYPE_SUBSCRIBE:
            parts.extend(encode_str(topic[0]) + encode_int(topic[1], 1) for topic in topics)
            self.suback_wait.append((packet_id, time(), topics))
        else:
            assert sub_type == TYPE_UNSUBSCRIBE
            parts.extend(map(encode_str, topics))
            self.unsuback_wait.append((packet_id, time(), topics))

        data = b"".join(parts)
        data_len = encode_varlen_int(len(data))
        with self.sock_lock:
            self.get_sock().send(header_data + data_len + data)
        self.last_activity = time()

    def subscribe(self, *topics):
        for topic, qos, cb in topics:
            self.callbacks[topic] = cb
        self.send_subscribe(topics, TYPE_SUBSCRIBE)

    def unsubscribe(self, *topics):
        self.send_subscribe(topics, TYPE_UNSUBSCRIBE)

    def send_pingreq(self):
        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = TYPE_PINGREQ
        with self.sock_lock:
            self.get_sock().send(header_data + b"\x00")
        self.last_activity = time()
        self.ping_wait += 1

    def disconnect(self):
        self.connected = False
        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = TYPE_DISCONNECT
        with self.sock_lock:
            try:
                self.get_sock().send(header_data + b"\x00")
                self.get_sock().close()
            except OSError:
                pass
            self.sock = None
        self.last_activity = time()

    def recv_connack(self, header):
        assert header.type == TYPE_CONNACK
        connack, connack_data = recv_struct(self.get_sock(), MQTTConnAckLayout)

        if connack_data.return_code != 0:
            if connack_data.return_code == 1:
                print("mqtt.recv_connack: ERROR unacceptable protocol version!")
            elif connack_data.return_code == 2:
                print("mqtt.recv_connack: ERROR identifier rejected")
            elif connack_data.return_code == 3:
                print("mqtt.recv_connack: ERROR Server unavailable")
            elif connack_data.return_code == 4:
                print("mqtt.recv_connack: ERROR bad user name or password")
            elif connack_data.return_code == 5:
                print("mqtt.recv_connack: ERROR not authorized")
            else:
                print("mqtt.recv_connack: ERROR unknown return code")
            self.wait_retry()
            self.connect()
            return

        if self.clean_session:
            if connack_data.session_present == 0:
                print("mqtt.recv_connack: WARNING unexpected session present")
            self.disconnect()
            self.clean_session = False
            self.connect()
        else:
            self.connected = True

    def recv_publish(self, header):
        assert header.type == TYPE_PUBLISH
        data_len = recv_varlen_int(self.get_sock())
        data = self.get_sock().recv(data_len)

        topic, data = decode_str(data)

        if header.qos != 0:
            packet_id, data = decode_int(data)
            self.inbound_wait.append((packet_id, time(), topic, data, header.retain == 1))
            self.send_puback(packet_id, TYPE_PUBACK if header.qos == 1 else TYPE_PUBREC)

    def recv_puback(self, header):
        puback, puback_data = recv_struct(self.get_sock(), MQTTAckRecvLayout)
        if header.type == TYPE_PUBREL:
            self.send_puback(puback.packet_id, TYPE_PUBCOMP)
        else:
            outbound_wait = (
                self.puback_wait if header.type == TYPE_PUBACK else
                self.pubrec_wait if header.type == TYPE_PUBREC else
                self.pubcomp_wait)

            try:
                packet_idx = [i[0] for i in outbound_wait].index(puback.packet_id)
            except ValueError:
                print(f"mqtt.recv_puback({header.type}): {puback.packet_id} not in {outbound_wait}")
                print(f"mqtt.recv_puback({header.type}): DEBUG {hexlify(puback_data)}")
                return

            packet_info = outbound_wait.pop(packet_idx)

            if header.type == TYPE_PUBREC:
                self.send_puback(puback.packet_id, TYPE_PUBREL)
                self.pubcomp_wait.append(packet_info)

    def recv_suback(self, header):
        suback, suback_data = recv_struct(self.get_sock(), MQTTAckRecvLayout)
        suback_wait = self.suback_wait if header.type == TYPE_SUBACK else self.unsuback_wait
        try:
            suback_wait.pop([i[0] for i in suback_wait].index(suback.packet_id))
        except ValueError:
            print(f"mqtt.recv_suback({header.type}): {suback.packet_id} not in {suback_wait}")
            print(f"mqtt.recv_suback({header.type}): DEBUG {hexlify(suback_data)}")
            pass

        for i in range(suback.length - 2):
            return_code = int.from_bytes(self.get_sock().recv(1), "big")
            if return_code > 2:
                print(f"mqtt.recv_suback({header.type}): Return code {return_code} > 2")
                print(f"mqtt.recv_suback({header.type}): DEBUG {hexlify(suback_data)}")

    def recv_pingresp(self, header):
        assert header.type == TYPE_PINGRESP
        self.get_sock().recv(1)
        self.ping_wait = 0

    @staticmethod
    def default_callback(client, topic, data, retained):
        print(f"{topic} = {data} (retained={retained})")

    RECV_HELPER = {
        TYPE_CONNACK: recv_connack,
        TYPE_PUBLISH: recv_publish,
        TYPE_PUBACK: recv_puback,
        TYPE_PUBREC: recv_puback,
        TYPE_PUBREL: recv_puback,
        TYPE_PUBCOMP: recv_puback,
        TYPE_SUBACK: recv_suback,
        TYPE_UNSUBACK: recv_suback,
        TYPE_PINGRESP: recv_pingresp,
    }

    def start(self):
        self.should_run = True
        start_new_thread(self.run, ())

    def run(self):
        with self.run_lock:
            while self.should_run:
                try:
                    self.connect()
                    while self.should_run:
                        sleep_ms(1)
                        self.process()
                except KeyError:
                    # Caught and released in process()
                    continue
                except OSError as e:
                    if e.errno == ECONNRESET:
                        continue
                    raise
                finally:
                    self.disconnect()

    def stop(self):
        self.should_run = False
        while self.run_lock.locked():
            pass

    def process(self):
        if self.connected and time() - self.last_activity > self.keepalive:
            self.send_pingreq()

        try:
            header, header_data = recv_struct(self.sock, MQTTHeaderLayout)
        except OSError as e:
            if e.errno == EAGAIN:
                return
            raise

        try:
            self.RECV_HELPER[header.type](self, header)
        except KeyError:
            print()
            print(f"mqtt.process: Unknown header type {header.type}")
            print(f"mqtt.process: DEBUG {hexlify(header_data)}")
            raise
