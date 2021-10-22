print("===IMPORTING captive_portal/dns/server.py===")
from socket import socket, AF_INET, SOCK_DGRAM

import uctypes

from .types import DNSHeaderLayout, DNSQuestionLayout
from .utils import get_question, get_answer


class DNSServer:
    def __init__(self, ip_addr, bind_addr=("0.0.0.0", 53)):
        print("===INITIALIZING DNS server===")
        self.ip_addr = ip_addr
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setblocking(False)
        self.socket.bind(bind_addr)

    def process(self):
        try:
            data, addr = self.socket.recvfrom(512)
        except OSError:
            return

        print()
        print(f"===PROCESSING DNS request from {addr}===")

        q_header = uctypes.struct(uctypes.addressof(data), DNSHeaderLayout, uctypes.BIG_ENDIAN)
        if q_header.QDCOUNT != 1:
            # TODO: reply with RCODE 4 (not implemented)
            print(f"===ERROR: expected 1 question, got {q_header.QDCOUNT}===")
            return False

        q_qd = get_question(data[12:])
        if q_qd.QTYPE != 1:
            # TODO: reply with RCODE 4 (not implemented)
            print(f"===ERROR: unknown QTYPE {q_qd.QTYPE}===")
            return False

        print("=====DEBUG=====")
        print(f"QNAME = {q_qd.QNAME}")

        r_header_buf = bytearray(12)
        r_header = uctypes.struct(uctypes.addressof(r_header_buf), DNSHeaderLayout, uctypes.BIG_ENDIAN)
        r_header.ID = q_header.ID
        r_header.flags.QR = 1
        r_header.flags.OPCODE = q_header.flags.OPCODE
        r_header.flags.RD = q_header.flags.RD
        r_header.QDCOUNT = q_header.QDCOUNT
        r_header.ANCOUNT = 1

        r_qd_buf = bytearray(4)
        r_qd = uctypes.struct(uctypes.addressof(r_qd_buf), DNSQuestionLayout, uctypes.BIG_ENDIAN)
        r_qd.QTYPE = q_qd.QTYPE
        r_qd.QCLASS = q_qd.QCLASS

        r_an = get_answer(q_qd, self.ip_addr)

        reply = r_header_buf + q_qd.QNAME + r_qd_buf + r_an
        self.socket.sendto(reply, addr)

        print(f"REPLY = {reply}")
        print("===END DEBUG===")

        print(f"===DONE: sent to {addr}===")


# if __name__ == "__main__":
#     dns_server = DNSServer("192.168.4.1", ("0.0.0.0", 8053))
#     while True:
#         dns_server.process()
