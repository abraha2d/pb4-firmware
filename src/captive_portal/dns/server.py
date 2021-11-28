from _thread import allocate_lock, start_new_thread
from errno import EAGAIN
from socket import AF_INET, SO_REUSEADDR, SOCK_DGRAM, SOL_SOCKET, getaddrinfo, socket

from uctypes import BIG_ENDIAN, addressof, struct
from utime import sleep_ms

from .types import DNSHeaderLayout
from .utils import get_qname_end, get_answer


class DNSServer:
    def __init__(self, ip_addr, bind_addr=getaddrinfo("0.0.0.0", 53, AF_INET, SOCK_DGRAM)[0][-1], start=True):
        self.answer = get_answer(ip_addr)
        self.bind_addr = bind_addr
        self.run_lock = allocate_lock()
        self.should_run = False

        if start:
            self.start()

    def start(self):
        self.should_run = True
        start_new_thread(self.run, ())

    def run(self):
        with self.run_lock:
            try:
                sock = socket(AF_INET, SOCK_DGRAM)
                sock.setblocking(False)
                sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                sock.bind(self.bind_addr)

                while self.should_run:
                    sleep_ms(1)
                    try:
                        self.process(sock)
                    except OSError as e:
                        if e.errno == -1:
                            continue
                        raise
            finally:
                sock.close()

    def stop(self):
        self.should_run = False
        while self.run_lock.locked():
            pass

    def process(self, sock):
        try:
            data, addr = sock.recvfrom(512)
        except OSError as e:
            if e.errno == EAGAIN:
                return
            raise

        header = struct(addressof(data), DNSHeaderLayout, BIG_ENDIAN)
        header.QR = 1
        header.QDCOUNT = 1
        header.ANCOUNT = 1
        header.NSCOUNT = 0
        header.ARCOUNT = 0

        qname_end = get_qname_end(data)
        response = data[:qname_end + 4] + self.answer
        sock.sendto(response, addr)
