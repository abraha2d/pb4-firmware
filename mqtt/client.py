from _thread import allocate_lock, start_new_thread
from socket import getaddrinfo, socket, AF_INET, SOCK_STREAM
from time import sleep

from uctypes import struct, addressof, BIG_ENDIAN

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
from .types import MQTTHeaderLayout, MQTTConnectFlagsLayout, MQTTConnackLayout, MQTTAckLayout
from .utils import write_varlen_int


class MQTTClient:
    def __init__(self, server="pb4_control.local", client_id=get_device_mac()):
        self.server = server
        self.client_id = client_id
        self.packet_id = 0

        self.run_lock = allocate_lock()
        self.should_run = False

    def get_packet_id(self):
        self.packet_id += 1
        if self.packet_id > 65536:
            self.packet_id = 1
        return self.packet_id

    def send_connect(self, sock, lwt=None, keepalive=0):
        header_data = bytes(2)
        header = struct(addressof(header_data), MQTTHeaderLayout, BIG_ENDIAN)
        header.type = TYPE_CONNECT

        flags_data = bytes(1)
        flags = struct(addressof(flags_data), MQTTConnectFlagsLayout, BIG_ENDIAN)

        keepalive_data = keepalive.to_bytes(2, "big")
        client_id_data = len(self.client_id).to_bytes(2, "big") + self.client_id.encode()

        data = PROTOCOL + flags_data + keepalive_data + client_id_data

        if lwt is not None:
            assert 0 <= lwt[2] <= 2

            flags.will = 1
            flags.will_qos = lwt[2]
            flags.will_retain = 1 if lwt[3] else 0

            will_topic_data = len(lwt[0]).to_bytes(2, "big") + lwt[0].encode()
            will_message_data = len(lwt[1]).to_bytes(2, "big") + lwt[1].encode()

            data += will_topic_data + will_message_data

        data_len = write_varlen_int(len(data))
        data = header_data + data_len + data
        sock.send(data)

    def recv_connack(self, sock):
        connack_data = sock.recv(4)
        connack = struct(addressof(connack_data), MQTTConnackLayout, BIG_ENDIAN)
        assert connack.header.type == TYPE_CONNACK
        assert connack.return_code == 0

    def send_publish(self, sock, topic, message, qos=0, retain=False):
        assert 0 <= qos <= 2

        header_data = bytes(2)
        header = struct(addressof(header_data), MQTTHeaderLayout, BIG_ENDIAN)
        header.type = TYPE_PUBLISH
        header.qos = qos
        header.retain = 1 if retain else 0

        topic_name_data = len(topic).to_bytes(2, "big") + topic.encode()
        packet_id = self.get_packet_id()
        packet_id_data = packet_id.to_bytes(2, "big")
        message_data = message.encode()

        data = topic_name_data + packet_id_data + message_data
        data_len = write_varlen_int(len(data))
        data = header_data + data_len + data
        sock.send(data)

        return packet_id

    def recv_puback(self, sock, packet_id, ack_type=TYPE_PUBACK):
        puback_data = sock.recv(4)
        puback = struct(addressof(puback_data), MQTTAckLayout, BIG_ENDIAN)
        assert puback.header.type == ack_type
        assert puback.packet_id == packet_id

    def send_pubrel(self, sock, packet_id):
        pubrel_data = bytes(4)
        pubrel = struct(addressof(pubrel_data), MQTTAckLayout, BIG_ENDIAN)
        pubrel.header.type = TYPE_PUBREL
        pubrel.header.qos = 1
        pubrel.length = 2
        pubrel.packet_id = packet_id
        sock.send(pubrel_data)

    def send_subscribe(self, sock, topics, sub_type=TYPE_SUBSCRIBE):
        assert len(topics) > 0

        header_data = bytes(2)
        header = struct(addressof(header_data), MQTTHeaderLayout, BIG_ENDIAN)
        header.type = sub_type
        header.qos = 1

        packet_id = self.get_packet_id()
        packet_id_data = packet_id.to_bytes(2, "big")

        topic_data = b""
        for topic in topics:
            assert 0 <= topic[1] <= 2
            topic_data += len(topic[0]).to_bytes(2, "big") + topic[0].encode() + topic[1].to_bytes(1, "big")

        data = packet_id_data + topic_data
        data_len = write_varlen_int(len(data))
        data = header_data + data_len + data
        sock.send(data)

        return packet_id

    def recv_suback(self, sock, packet_id, ack_type=TYPE_SUBACK):
        suback_data = sock.recv(4)
        suback = struct(addressof(suback_data), MQTTAckLayout, BIG_ENDIAN)
        assert suback.header.type == ack_type
        assert suback.packet_id == packet_id

        for i in range(suback.length - 2):
            return_code = sock.recv(1)
            assert return_code != b"\x80"

    def send_pingreq(self, sock):
        header_data = bytes(2)
        header = struct(addressof(header_data), MQTTHeaderLayout, BIG_ENDIAN)
        header.type = TYPE_PINGREQ
        sock.send(header_data)

    def recv_pingresp(self, sock):
        header_data = sock.recv(2)
        header = struct(addressof(header_data), MQTTHeaderLayout, BIG_ENDIAN)
        assert header.type == TYPE_PINGRESP

    def send_disconnect(self, sock):
        header_data = bytes(2)
        header = struct(addressof(header_data), MQTTHeaderLayout, BIG_ENDIAN)
        header.type = TYPE_DISCONNECT
        sock.send(header_data)

    def connect(self, sock):
        lwt = [
            f"/pb4/devices/{self.client_id}/status",
            "0",
            1,
            True,
        ]
        self.send_connect(sock, lwt=lwt, keepalive=10)
        self.recv_connack(sock)

    def publish(self, sock, topic, message, qos=0, retain=False):
        assert 0 <= qos <= 2
        pid = self.send_publish(sock, topic, message, qos, retain)
        if qos == 1:
            self.recv_puback(sock, pid)
        elif qos == 2:
            self.recv_puback(sock, pid, TYPE_PUBREC)
            self.send_pubrel(sock, pid)
            self.recv_puback(sock, pid, TYPE_PUBCOMP)

    def subscribe(self, sock, topics):
        pid = self.send_subscribe(sock, topics)
        self.recv_suback(sock, pid)

    def unsubscribe(self, sock, topics):
        topic_list = [(topic,) for topic in topics]
        pid = self.send_subscribe(sock, topic_list, TYPE_UNSUBSCRIBE)
        self.recv_suback(sock, pid, TYPE_UNSUBACK)

    def ping(self, sock):
        self.send_pingreq(sock)
        self.recv_pingresp(sock)

    def start(self):
        self.should_run = True
        start_new_thread(self.run, ())

    def run(self):
        with self.run_lock:
            try:
                sockaddr = getaddrinfo(self.server, 1883)[0][-1]
                sock = socket(AF_INET, SOCK_STREAM)
                sock.setblocking(False)
                sock.connect(sockaddr)
                self.connect(sock)

                while True:
                    sleep(1)
                    self.ping(sock)
            finally:
                sock.close()

    def stop(self):
        self.should_run = False
        while self.run_lock.locked():
            pass

    def process(self, sock):
        pass
