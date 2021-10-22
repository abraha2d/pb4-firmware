from uctypes import BF_LEN, BF_POS, BFUINT16, UINT16, UINT32


DNSHeaderLayout = {
    "ID": 0 | UINT16,
    "QR": 2 | BFUINT16 | 15 << BF_POS | 1 << BF_LEN,
    "OPCODE": 2 | BFUINT16 | 11 << BF_POS | 4 << BF_LEN,
    "AA": 2 | BFUINT16 | 10 << BF_POS | 1 << BF_LEN,
    "TC": 2 | BFUINT16 | 9 << BF_POS | 1 << BF_LEN,
    "RD": 2 | BFUINT16 | 8 << BF_POS | 1 << BF_LEN,
    "RA": 2 | BFUINT16 | 7 << BF_POS | 1 << BF_LEN,
    "Z": 2 | BFUINT16 | 4 << BF_POS | 3 << BF_LEN,
    "RCODE": 2 | BFUINT16 | 0 << BF_POS | 4 << BF_LEN,
    "QDCOUNT": 4 | UINT16,
    "ANCOUNT": 6 | UINT16,
    "NSCOUNT": 8 | UINT16,
    "ARCOUNT": 10 | UINT16,
}


DNSAnswerExtraLayout = {
    "TTL": 0 | UINT32,
    "RDLENGTH": 4 | UINT16,
}
