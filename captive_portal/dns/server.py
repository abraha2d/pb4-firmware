from socket import socket, AF_INET, SOCK_DGRAM
from uctypes import BIG_ENDIAN, addressof, struct

from .types import DNSHeaderLayout
from .utils import get_qname_end, get_answer


class DNSServer:
    def __init__(self, ip_addr, bind_addr=("0.0.0.0", 53)):
        self.answer = get_answer(ip_addr)

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setblocking(False)
        self.socket.bind(bind_addr)

    def process(self):
        try:
            data, addr = self.socket.recvfrom(512)
        except OSError:
            return

        print(f"DNS query from {addr}")

        header = struct(addressof(data), DNSHeaderLayout, BIG_ENDIAN)
        header.QR = 1
        header.QDCOUNT = 1
        header.ANCOUNT = 1
        header.NSCOUNT = 0
        header.ARCOUNT = 0

        qname_end = get_qname_end(data)
        question = data[12:qname_end+4]
        print(f"- QUESTION: {question}")

        response = data[:qname_end+4] + self.answer
        print(f"- RESPONSE: {response}")

        self.socket.sendto(response, addr)


# if __name__ == "__main__":
#     dns_server = DNSServer("192.168.4.1", ("0.0.0.0", 8053))
#     while True:
#         dns_server.process()
