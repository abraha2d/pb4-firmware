print("===IMPORTING captive_portal/dns/types.py===")
import uctypes

DNSHeaderFlagsLayout = {
    "QR": 0 | uctypes.BFUINT16 | 15 << uctypes.BF_POS | 1 << uctypes.BF_LEN,
    "OPCODE": 0 | uctypes.BFUINT16 | 11 << uctypes.BF_POS | 4 << uctypes.BF_LEN,
    "AA": 0 | uctypes.BFUINT16 | 10 << uctypes.BF_POS | 1 << uctypes.BF_LEN,
    "TC": 0 | uctypes.BFUINT16 | 9 << uctypes.BF_POS | 1 << uctypes.BF_LEN,
    "RD": 0 | uctypes.BFUINT16 | 8 << uctypes.BF_POS | 1 << uctypes.BF_LEN,
    "RA": 0 | uctypes.BFUINT16 | 7 << uctypes.BF_POS | 1 << uctypes.BF_LEN,
    "Z": 0 | uctypes.BFUINT16 | 4 << uctypes.BF_POS | 3 << uctypes.BF_LEN,
    "RCODE": 0 | uctypes.BFUINT16 | 0 << uctypes.BF_POS | 4 << uctypes.BF_LEN,
}


DNSHeaderLayout = {
    "ID": 0 | uctypes.UINT16,
    "flags": (2, DNSHeaderFlagsLayout),
    "QDCOUNT": 4 | uctypes.UINT16,
    "ANCOUNT": 6 | uctypes.UINT16,
    "NSCOUNT": 8 | uctypes.UINT16,
    "ARCOUNT": 10 | uctypes.UINT16,
}


DNSQuestionLayout = {
    "QTYPE": 0 | uctypes.UINT16,
    "QCLASS": 2 | uctypes.UINT16,
}


class DNSQuestion:
    pass


DNSAnswerLayout = {
    "TYPE": 0 | uctypes.UINT16,
    "CLASS": 2 | uctypes.UINT16,
    "TTL": 4 | uctypes.UINT32,
    "RDLENGTH": 8 | uctypes.UINT16,
}
