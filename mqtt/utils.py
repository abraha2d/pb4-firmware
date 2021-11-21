def read_varlen_int(sock):
    multiplier = 1
    value = 0
    while True:
        byte = sock.read(1)
        value += (byte & 127) * multiplier
        if byte & 128 == 0:
            return value
        multiplier *= 128


def write_varlen_int(i):
    parts = []
    while i > 0:
        byte = i % 128
        i = i // 128
        if i > 0:
            byte = byte | 128
        parts.append(byte)
    return bytes(bytes)
