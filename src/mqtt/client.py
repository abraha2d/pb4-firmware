import gc
from binascii import hexlify
from errno import ECONNABORTED, ECONNRESET, EHOSTUNREACH, ENOENT, ENOTCONN
from socket import getaddrinfo
from time import time

# noinspection PyUnresolvedReferences
from uasyncio import (
    Event,
    Lock,
    core,
    create_task,
    current_task,
    get_event_loop,
    open_connection,
    sleep_ms,
)

from .constants import (
    PROTOCOL,
    RETRY_INTERVAL,
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

errnos = [
    ECONNABORTED,
    ECONNRESET,
    EHOSTUNREACH,
    23,  # ENFILE
    ENOENT,
    ENOTCONN,
    -2,  # ???
    -259,  # ESP_ERR_INVALID_STATE ?
]


class MQTTClient:
    def __init__(
        self,
        server: str,
        client_id: str,
        lwt=None,
        bc=None,  # birth certificate (i.e. opposite of last will and testament)
        username=None,
        password=None,
        keepalive=0,
    ):
        self.server = server
        self.client_id = client_id
        self.clean_session = True
        self.lwt = lwt
        self.bc = bc
        self.username = username
        self.password = password
        self.keepalive = keepalive

        self.sock = None
        self.sock_lock = Lock()

        self.connected = Event()
        self.last_activity = time()
        self.packet_id = 0
        self.retry_interval = RETRY_INTERVAL

        self.puback_wait = []
        self.pubrec_wait = []
        self.pubcomp_wait = []
        self.suback_wait = []
        self.unsuback_wait = []

        self.inbound_wait = []
        self.ping_wait = 0

        self.callbacks = {}

    def get_packet_id(self):
        self.packet_id += 1
        if self.packet_id > 65536:
            self.packet_id = 1
        return self.packet_id

    async def get_sock(self):
        if self.sock is None:
            self.connected.clear()
            while True:
                try:
                    # workaround for https://github.com/micropython/micropython/issues/8038
                    # TODO: remove once fixed upstream
                    ai = getaddrinfo(self.server, 1883)[0][-1]
                    self.sock = await open_connection(*ai)
                    break
                except OSError as e:
                    if e.errno not in errnos:
                        raise
                await self.wait_retry()
            self.retry_interval = RETRY_INTERVAL
        return self.sock

    async def wait_retry(self):
        print(f"mqtt.wait_retry: Retrying after {self.retry_interval} ms...")
        await sleep_ms(self.retry_interval)
        if self.retry_interval < 4000:
            self.retry_interval *= 2

    async def connect(self):
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
        async with self.sock_lock:
            reader, writer = await self.get_sock()
            writer.write(header_data + data_len + data)
            await writer.drain()
        self.last_activity = time()

    async def send_publish(self, topic: str, message: str, qos: int, retain: bool):
        await self.connected.wait()

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
        async with self.sock_lock:
            reader, writer = await self.get_sock()
            writer.write(header_data + data_len + data)
            await writer.drain()
        self.last_activity = time()

    async def publish(self, topic: str, message: str, qos=0, retain=False):
        sent = False
        while not sent:
            try:
                await self.send_publish(topic, message, qos, retain)
                sent = True
            except OSError as e:
                if e.errno not in errnos:
                    raise
            await self.wait_retry()
        self.retry_interval = RETRY_INTERVAL

    async def send_puback(self, pid, ack_type):
        puback, puback_data = new_struct(MQTTAckSendLayout)
        puback.header.type = ack_type
        if ack_type == TYPE_PUBREL:
            puback.header.qos = 1
        puback.length = 2
        puback.packet_id = pid
        async with self.sock_lock:
            reader, writer = await self.get_sock()
            writer.write(puback_data)
            await writer.drain()
        self.last_activity = time()

        if ack_type == TYPE_PUBACK or ack_type == TYPE_PUBCOMP:
            try:
                packet_idx = [i[0] for i in self.inbound_wait].index(pid)
            except ValueError:
                print(f"mqtt.send_puback: WARNING just acked an unknown packet!")
                return

            pid, packet_time, topic, data, retained = self.inbound_wait.pop(packet_idx)

            try:
                topic = topic.decode()
            except UnicodeError:
                print(f"mqtt.send_puback: UnicodeError when trying to decode topic")
                print(f"mqtt.send_puback: DEBUG {topic}")

            cb = self.callbacks.get(topic, self.default_callback)
            try:
                await cb(self, topic, data, retained)
            except Exception as e:
                get_event_loop().call_exception_handler(
                    {
                        "message": "mqtt.send_puback: Error during callback!",
                        "future": current_task(),
                        "exception": e,
                    }
                )

    async def send_subscribe(self, topics, sub_type):
        await self.connected.wait()

        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = sub_type
        header.qos = 1

        packet_id = self.get_packet_id()
        parts = [encode_int(packet_id)]

        if sub_type == TYPE_SUBSCRIBE:
            part = (encode_str(topic[0]) + encode_int(topic[1], 1) for topic in topics)
            parts.extend(part)
            self.suback_wait.append((packet_id, time(), topics))
        else:
            assert sub_type == TYPE_UNSUBSCRIBE
            parts.extend(map(encode_str, topics))
            self.unsuback_wait.append((packet_id, time(), topics))

        data = b"".join(parts)
        data_len = encode_varlen_int(len(data))
        async with self.sock_lock:
            reader, writer = await self.get_sock()
            writer.write(header_data + data_len + data)
            await writer.drain()
        self.last_activity = time()

    async def subscribe(self, *topics):
        sent = False
        while not sent:
            try:
                for topic, qos, cb in topics:
                    self.callbacks[topic] = cb
                await self.send_subscribe(topics, TYPE_SUBSCRIBE)
                sent = True
            except OSError as e:
                if e.errno not in errnos:
                    raise
            await self.wait_retry()
        self.retry_interval = RETRY_INTERVAL

    async def unsubscribe(self, *topics):
        sent = False
        while not sent:
            try:
                await self.send_subscribe(topics, TYPE_UNSUBSCRIBE)
                sent = True
            except OSError as e:
                if e.errno not in errnos:
                    raise
            self.wait_retry()
        self.retry_interval = RETRY_INTERVAL

    async def send_pingreq(self):
        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = TYPE_PINGREQ
        async with self.sock_lock:
            reader, writer = await self.get_sock()
            writer.write(header_data + b"\x00")
            await writer.drain()
        self.last_activity = time()
        self.ping_wait += 1

    async def disconnect(self):
        self.connected.clear()
        header, header_data = new_struct(MQTTHeaderLayout)
        header.type = TYPE_DISCONNECT
        async with self.sock_lock:
            try:
                reader, writer = await self.get_sock()
                writer.write(header_data + b"\x00")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except OSError:  # TODO: Cast a smaller net
                pass
            self.sock = None
        self.last_activity = time()

    async def recv_connack(self, header):
        assert header.type == TYPE_CONNACK
        reader, writer = await self.get_sock()
        connack, connack_data = await recv_struct(reader, MQTTConnAckLayout)

        if connack.return_code != 0:
            if connack.return_code == 1:
                print("mqtt.recv_connack: ERROR unacceptable protocol version!")
            elif connack.return_code == 2:
                print("mqtt.recv_connack: ERROR identifier rejected")
            elif connack.return_code == 3:
                print("mqtt.recv_connack: ERROR Server unavailable")
            elif connack.return_code == 4:
                print("mqtt.recv_connack: ERROR bad user name or password")
            elif connack.return_code == 5:
                print("mqtt.recv_connack: ERROR not authorized")
            else:
                print("mqtt.recv_connack: ERROR unknown return code")
            await self.wait_retry()
            await self.connect()
            return
        self.retry_interval = RETRY_INTERVAL

        if self.clean_session:
            if connack.session_present == 1:
                print("mqtt.recv_connack: WARNING unexpected session present")
            await self.disconnect()
            self.clean_session = False
            await self.connect()
        else:
            self.connected.set()
            await self.publish(*self.bc)

    @staticmethod
    async def bulk_read(reader, n):
        gc.collect()
        r = bytearray(n)
        mv = memoryview(r)
        while n:
            yield core._io_queue.queue_read(reader.s)
            r2 = reader.s.readinto(mv[-n:], n)
            if not r2:
                raise EOFError
            n -= r2
        return r

    async def recv_publish(self, header):
        assert header.type == TYPE_PUBLISH
        reader, writer = await self.get_sock()
        data_len = await recv_varlen_int(reader)
        if data_len > 1024:
            print(f"mqtt.recv_publish: Receiving {data_len} bytes...")
        data = await self.bulk_read(reader, data_len)

        topic, data = decode_str(data)

        if header.qos > 0:
            packet_id, data = decode_int(data)
            self.inbound_wait.append(
                (
                    packet_id,
                    time(),
                    topic,
                    data,
                    header.retain == 1,
                )
            )
            await self.send_puback(
                packet_id,
                TYPE_PUBACK if header.qos == 1 else TYPE_PUBREC,
            )
        else:
            try:
                topic = topic.decode()
            except UnicodeError:
                print(f"mqtt.recv_publish: UnicodeError when trying to decode topic")
                print(f"mqtt.recv_publish: DEBUG {topic}")

            cb = self.callbacks.get(topic, self.default_callback)
            try:
                await cb(self, topic, data, header.retain == 1)
            except Exception as e:
                get_event_loop().call_exception_handler(
                    {
                        "message": "mqtt.recv_publish: Error during callback!",
                        "future": current_task(),
                        "exception": e,
                    }
                )

    async def recv_puback(self, header):
        reader, writer = await self.get_sock()
        puback, puback_data = await recv_struct(reader, MQTTAckRecvLayout)
        if header.type == TYPE_PUBREL:
            await self.send_puback(puback.packet_id, TYPE_PUBCOMP)
        else:
            outbound_wait = (
                self.puback_wait
                if header.type == TYPE_PUBACK
                else self.pubrec_wait
                if header.type == TYPE_PUBREC
                else self.pubcomp_wait
            )

            try:
                packet_idx = [i[0] for i in outbound_wait].index(puback.packet_id)
            except ValueError:
                print(
                    f"mqtt.recv_puback({header.type}): "
                    + f"WARNING {puback.packet_id} not in {outbound_wait}"
                )
                print(
                    f"mqtt.recv_puback({header.type}): "
                    + f"DEBUG {hexlify(puback_data).decode()}"
                )
                return

            packet_info = outbound_wait.pop(packet_idx)

            if header.type == TYPE_PUBREC:
                await self.send_puback(puback.packet_id, TYPE_PUBREL)
                self.pubcomp_wait.append(packet_info)

    async def recv_suback(self, header):
        reader, writer = await self.get_sock()
        suback, suback_data = await recv_struct(reader, MQTTAckRecvLayout)
        wait = self.suback_wait if header.type == TYPE_SUBACK else self.unsuback_wait
        try:
            wait.pop([i[0] for i in wait].index(suback.packet_id))
        except ValueError:
            print(
                f"mqtt.recv_suback({header.type}): "
                + f"WARNING {suback.packet_id} not in {wait}"
            )
            print(
                f"mqtt.recv_suback({header.type}): "
                + f"DEBUG {hexlify(suback_data).decode()}"
            )

        for i in range(suback.length - 2):
            byte = await reader.readexactly(1)
            return_code = int.from_bytes(byte, "big")
            if return_code > 2:
                print(
                    f"mqtt.recv_suback({header.type}): "
                    + f"WARNING return code {return_code} > 2"
                )
                print(
                    f"mqtt.recv_suback({header.type}): "
                    + f"DEBUG {hexlify(suback_data).decode()}"
                )

    async def recv_pingresp(self, header):
        assert header.type == TYPE_PINGRESP
        reader, writer = await self.get_sock()
        await reader.readexactly(1)
        self.ping_wait = 0

    # noinspection PyUnusedLocal
    @staticmethod
    async def default_callback(client, topic, data, retained):
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

    async def run(self):
        keepalive_task = create_task(self.process_keepalive())
        while True:
            try:
                await self.connect()
                self.retry_interval = RETRY_INTERVAL
                while True:
                    await self.process_receive()
            except KeyError:
                # Caught and released in process_receive()
                continue
            except EOFError:
                continue
            except OSError as e:
                if e.errno in errnos:
                    continue
                raise
            finally:
                await self.disconnect()
            await self.wait_retry()

    async def process_keepalive(self):
        while True:
            if self.connected.is_set():
                time_to_ping = self.keepalive - (time() - self.last_activity)
                if time_to_ping <= 0:
                    try:
                        await self.send_pingreq()
                    except EOFError:
                        continue
                    except OSError as e:
                        if e.errno not in errnos:
                            raise
                else:
                    await sleep_ms(time_to_ping * 1000)
            else:
                await self.connected.wait()

    async def process_receive(self):
        reader, writer = await self.get_sock()
        header, header_data = await recv_struct(reader, MQTTHeaderLayout)

        try:
            await self.RECV_HELPER[header.type](self, header)
        except KeyError:
            print()
            print(f"mqtt.process_receive: Unknown header type {header.type}")
            print(f"mqtt.process_receive: DEBUG {hexlify(header_data).decode()}")
            raise
