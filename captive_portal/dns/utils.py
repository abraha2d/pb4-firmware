from uctypes import BIG_ENDIAN, addressof, struct

from .types import DNSAnswerLayout


def get_qname_end(data):
    i = 12
    while True:
        length = data[i]
        i += length + 1
        if length == 0:
            return i


def get_answer(ip_address):
    an_buf = bytearray(16)
    an = struct(addressof(an_buf), DNSAnswerLayout, BIG_ENDIAN)

    an.ONES = 0b11
    an.OFFSET = 12

    an.TYPE = 1
    an.CLASS = 1
    an.TTL = 15
    an.RDLENGTH = 4

    b1, b2, b3, b4 = ip_address.split(".")
    an.RDATA1 = int(b1)
    an.RDATA2 = int(b2)
    an.RDATA3 = int(b3)
    an.RDATA4 = int(b4)

    return an_buf
