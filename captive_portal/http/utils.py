def url_decode(enc):
    if "=" in enc:
        return [url_decode(e) for e in enc.split("=")]

    dec = enc.replace("+", " ")

    if "%" in enc:
        parts = dec.split("%")
        dec = parts[0] + "".join(chr(int(bit[:2], 16)) + bit[2:] for bit in parts[1:])

    return dec
