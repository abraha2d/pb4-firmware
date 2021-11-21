from _thread import allocate_lock, start_new_thread
from socket import getaddrinfo, socket, AF_INET, SOCK_STREAM

from uctypes import struct, addressof, BIG_ENDIAN

from utils import get_device_mac
from .constants import TYPE_CONNECT, PROTOCOL, TYPE_CONNACK, TYPE_PUBLISH, TYPE_PUBACK, TYPE_PUBREL
from .types import MQTTHeaderLayout, MQTTConnectFlagsLayout, MQTTConnackLayout, MQTTPubackLayout
from .utils import write_varlen_int


class MQTTClient:
    def __init__(self, server="pb4_control.local", client_id=get_device_mac()):
        self.server = server
        self.client_id = client_id
        self.packet_id = 0

        self.run_lock = allocate_lock()
        self.should_run = False

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
            finally:
                sock.close()

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
            flags.will = 1
            flags.will_qos = lwt[2]
            flags.will_retain = lwt[3]

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
        header_data = bytes(2)
        header = struct(addressof(header_data), MQTTHeaderLayout, BIG_ENDIAN)
        header.type = TYPE_PUBLISH
        header.qos = qos
        header.retain = 1 if retain else 0

        topic_name_data = len(topic).to_bytes(2, "big") + topic.encode()
        packet_id_data = self.get_packet_id().to_bytes(2, "big")
        message_data = message.encode()

        data = topic_name_data + packet_id_data + message_data
        data_len = write_varlen_int(len(data))
        data = header_data + data_len + data
        sock.send(data)

    def recv_puback(self, sock, ack_type=TYPE_PUBACK):
        puback_data = sock.recv(4)
        puback = struct(addressof(puback_data), MQTTPubackLayout, BIG_ENDIAN)
        assert puback.header.type == ack_type
        assert puback.packet_id == self.packet_id

    def send_pubrel(self, sock):
        pubrel_data = bytes(4)
        pubrel = struct(addressof(pubrel_data), MQTTPubackLayout, BIG_ENDIAN)
        pubrel.header.type = TYPE_PUBREL
        pubrel.header.qos = 1
        pubrel.length = 2
        pubrel.packet_id = self.packet_id
        sock.send(pubrel_data)

    def get_packet_id(self):
        self.packet_id += 1
        if self.packet_id > 65536:
            self.packet_id = 1
        return self.packet_id

    def stop(self):
        self.should_run = False
        while self.run_lock.locked():
            pass
