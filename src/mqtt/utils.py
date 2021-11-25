from uctypes import BIG_ENDIAN, addressof, sizeof, struct


def new_struct(layout, data=None):
    if data is None:
        data = bytes(sizeof(layout, BIG_ENDIAN))
    s = struct(addressof(data), layout, BIG_ENDIAN)
    return s, data


def recv_struct(sock, layout):
    data = sock.recv(sizeof(layout, BIG_ENDIAN))
    return new_struct(layout, data)


def encode_int(i, s=2):
    return i.to_bytes(s, "big")


def decode_int(data):
    i = int.from_bytes(data[:2], "big")
    return i, data[2:]


def encode_varlen_int(i):
    parts = []
    while i > 0:
        byte = i % 128
        i = i // 128
        if i > 0:
            byte = byte | 128
        parts.append(byte)
    return bytes(parts)


def recv_varlen_int(sock):
    multiplier = 1
    value = 0
    while True:
        byte = int.from_bytes(sock.read(1), "big")
        value += (byte & 127) * multiplier
        if byte & 128 == 0:
            return value
        multiplier *= 128


def encode_str(s):
    return encode_int(len(s)) + s.encode()


def decode_str(data):
    str_len, data = decode_int(data)
    return data[:str_len], data[str_len:]
