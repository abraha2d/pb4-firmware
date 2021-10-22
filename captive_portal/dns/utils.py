print("===IMPORTING captive_portal/dns/utils.py===")
import uctypes

from .types import DNSQuestion, DNSQuestionLayout, DNSAnswerLayout


def get_question(data):
    qname = b""
    while True:
        length = data[0]
        qname += data[:1 + length]
        data = data[1 + length:]
        if length == 0:
            qd_struct = uctypes.struct(uctypes.addressof(data), DNSQuestionLayout, uctypes.BIG_ENDIAN)
            qd = DNSQuestion()
            qd.QNAME = qname
            qd.QTYPE = qd_struct.QTYPE
            qd.QCLASS = qd_struct.QCLASS
            qd.struct = qd_struct
            return qd


def get_answer(qd, ip_address):
    an_buf = bytearray(10)
    an = uctypes.struct(uctypes.addressof(an_buf), DNSAnswerLayout, uctypes.BIG_ENDIAN)

    an.TYPE = qd.QTYPE
    an.CLASS = qd.QCLASS
    an.TTL = 1
    an.RDLENGTH = 4

    rdata = bytes(int(i) for i in ip_address.split("."))
    return qd.QNAME + an_buf + rdata
