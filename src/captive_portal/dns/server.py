from socket import AF_INET, SO_REUSEADDR, SOCK_DGRAM, SOL_SOCKET, getaddrinfo, socket

from uasyncio import core
from uctypes import BIG_ENDIAN, addressof, struct

from .types import DNSHeaderLayout
from .utils import get_qname_end, get_answer


class DNSServer:
    def __init__(self, ip_addr):
        self.answer = get_answer(ip_addr)

    async def serve(self):
        ai = getaddrinfo("0.0.0.0", 53)[0]  # TODO this is blocking!
        s = socket(AF_INET, SOCK_DGRAM)
        s.setblocking(False)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind(ai[-1])

        while True:
            try:
                yield core._io_queue.queue_read(s)
            except core.CancelledError:
                s.close()
                return

            data, addr = s.recvfrom(512)

            header = struct(addressof(data), DNSHeaderLayout, BIG_ENDIAN)
            header.QR = 1
            header.QDCOUNT = 1
            header.ANCOUNT = 1
            header.NSCOUNT = 0
            header.ARCOUNT = 0

            qname_end = get_qname_end(data)
            response = data[: qname_end + 4] + self.answer
            s.sendto(response, addr)
