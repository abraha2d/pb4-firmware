from _thread import allocate_lock, start_new_thread
from errno import EAGAIN, ECONNRESET
from socket import getaddrinfo, socket, AF_INET, SOCK_STREAM

from utime import sleep_ms, time

from utils import get_device_mac
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
            server="pb4_control.local",
            client_id=get_device_mac(),
            clean_session=False,
            lwt=None,
            username=None,
            password=None,
            keepalive=0,
    ):
        self.server = server
        self.client_id = client_id
        self.clean_session = clean_session
        self.lwt = lwt
        self.username = username
        self.password = password
        self.keepalive = keepalive

        self.sock = None
        self.connected = False
        self.last_activity = time()
        self.packet_id = 0
        self.pings = 0

        self.publishes = []
        self.subscribes = []
        self.unsubscribes = []

        self.run_lock = allocate_lock()
        self.should_run = False

    def get_packet_id(self):
        self.packet_id += 1
        if self.packet_id > 65536:
            self.packet_id = 1
        return self.packet_id

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
        self.sock.send(header_data + data_len + data)
        self.last_activity = time()
        self.connected = False

    def publish(self, topic, message, qos=0, retain=False):
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
            self.publishes.append(packet_id)
        data += message

        data_len = encode_varlen_int(len(data))
        self.sock.send(header_data + data_len + data)
        self.last_activity = time()

    def send_puback(self, packet_id, ack_type):
        puback, puback_data = new_struct(MQTTAckSendLayout)
        puback.header.type = ack_type
        if ack_type == TYPE_PUBREL:
            puback.header.qos = 1
        puback.length = 2
        puback.packet_id = packet_id
        self.sock.send(puback_data)
        self.last_activity = time()

    def send_subscribe(self, topics, sub_type):
        while not self.connected:
            sleep_ms(1)

        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = sub_type
        header.qos = 1

        packet_id = self.get_packet_id()
        parts = [encode_int(packet_id)]

        if sub_type == TYPE_SUBSCRIBE:
            parts.extend(encode_str(topic[0]) + encode_int(topic[1], 1) for topic in topics)
            self.subscribes.append(packet_id)
        else:
            assert sub_type == TYPE_UNSUBSCRIBE
            parts.extend(map(encode_str, topics))
            self.unsubscribes.append(packet_id)

        data = b"".join(parts)
        data_len = encode_varlen_int(len(data))
        self.sock.send(header_data + data_len + data)
        self.last_activity = time()

    def subscribe(self, topics):
        self.send_subscribe(topics, TYPE_SUBSCRIBE)

    def unsubscribe(self, topics):
        self.send_subscribe(topics, TYPE_UNSUBSCRIBE)

    def send_pingreq(self):
        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = TYPE_PINGREQ
        self.sock.send(header_data + b"\x00")
        self.last_activity = time()
        self.pings += 1

    def send_disconnect(self):
        self.connected = False
        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = TYPE_DISCONNECT
        self.sock.send(header_data + b"\x00")
        self.last_activity = time()

    def recv_connack(self, header):
        assert header.type == TYPE_CONNACK
        connack, connack_data = recv_struct(self.sock, MQTTConnAckLayout)
        # TODO: Handle unexpected session present
        # TODO: Handle return code != 0
        self.connected = True

    def recv_publish(self, header):
        assert header.type == TYPE_PUBLISH
        data_len = recv_varlen_int(self.sock)
        data = self.sock.recv(data_len)

        topic, data = decode_str(data)

        if header.qos != 0:
            packet_id, data = decode_int(data)
            self.send_puback(packet_id, TYPE_PUBREC if header.qos == 2 else TYPE_PUBACK)

        print(f"{topic} = {data} (qos={header.qos}, retain={header.retain})")
        return topic, data, header.qos, header.retain == 1

    def recv_puback(self, header):
        puback, puback_data = recv_struct(self.sock, MQTTAckRecvLayout)
        if header.type == TYPE_PUBACK or header.type == TYPE_PUBCOMP:
            try:
                self.publishes.remove(puback.packet_id)
            except ValueError:
                # TODO: Handle "object not in sequence"
                print(f"mqtt.recv_puback({header.type}): {puback.packet_id} not in {self.publishes}")
                print(f"mqtt.recv_puback({header.type}): DEBUG {puback_data}")
                pass
        else:
            assert header.type == TYPE_PUBREC or header.type == TYPE_PUBREL
            self.send_puback(puback.packet_id, header.type + 1)

    def recv_suback(self, header):
        suback, suback_data = recv_struct(self.sock, MQTTAckRecvLayout)
        try:
            if header.type == TYPE_SUBACK:
                self.subscribes.remove(suback.packet_id)
            else:
                assert header.type == TYPE_UNSUBACK
                self.unsubscribes.remove(suback.packet_id)
        except ValueError:
            # TODO: Handle "object not in sequence"
            print(f"mqtt.recv_suback({header.type}): {suback.packet_id} not in " +
                  f"{self.subscribes if header.type == TYPE_SUBACK else self.unsubscribes}")
            print(f"mqtt.recv_suback({header.type}): DEBUG {suback_data}")
            pass

        for i in range(suback.length - 2):
            return_code = int.from_bytes(self.sock.recv(1), "big")
            # TODO: Handle return code
            if return_code > 2:
                print(f"mqtt.recv_suback({header.type}): Return code {return_code} > 2")
                print(f"mqtt.recv_suback({header.type}): DEBUG {suback_data}")

    def recv_pingresp(self, header):
        self.sock.recv(1)
        assert header.type == TYPE_PINGRESP
        self.pings -= 1

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
                    sockaddr = getaddrinfo(self.server, 1883)[0][-1]
                    self.sock = socket(AF_INET, SOCK_STREAM)
                    self.sock.connect(sockaddr)

                    self.connect()

                    self.sock.setblocking(False)
                    while self.should_run:
                        sleep_ms(1)
                        self.process()
                except KeyError:
                    continue
                except OSError as e:
                    if e.errno == ECONNRESET:
                        continue
                    raise
                finally:
                    try:
                        self.send_disconnect()
                    except OSError:
                        pass
                    self.sock.close()
                    self.sock = None

    def stop(self):
        self.should_run = False
        while self.run_lock.locked():
            pass

    def process(self):
        if time() - self.last_activity > self.keepalive:
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
            print(f"mqtt.process: DEBUG {header_data}")
            raise
