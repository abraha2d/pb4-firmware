from uctypes import BIG_ENDIAN, addressof, struct

from .types import DNSAnswerExtraLayout


def get_qname_end(data):
    i = 12
    while True:
        length = data[i]
        i += length + 1
        if length == 0:
            return i


def get_answer(ip_address):
    an_buf = bytearray(6)
    an = struct(addressof(an_buf), DNSAnswerExtraLayout, BIG_ENDIAN)
    an.TTL = 15
    an.RDLENGTH = 4

    rdata = bytes(int(i) for i in ip_address.split("."))
    return an_buf + rdata
