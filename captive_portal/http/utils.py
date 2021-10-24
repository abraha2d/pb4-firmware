def url_decode(enc):
    if "=" in enc:
        parts = enc.split("=", 1)
        return url_decode(parts[0]), url_decode(parts[1])

    dec = enc.replace("+", " ")

    if "%" in enc:
        parts = dec.split("%")
        dec = parts[0] + "".join(chr(int(bit[:2], 16)) + bit[2:] for bit in parts[1:])

    return dec
