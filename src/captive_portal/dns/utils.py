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

    # noinspection PyUnresolvedReferences
    an.RDATA[:] = bytes(int(i) for i in ip_address.split("."))  # inet_pton doesn't seem to exist

    return an_buf
