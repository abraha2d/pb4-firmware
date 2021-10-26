from binascii import hexlify
from json import dumps
from time import sleep

from .server import HTTPServer
from .views import file_view


def get_mac_address(p, q, h):
    sleep(1)
    return 200, {}, "4c:11:ae:db:d5:a8"


def scan(p, q, h):
    sleep(2)
    results = [
        [b"WHF Blue", b'\x88\xdc\x96_*\xde', 11, -62, 3, False],
        [b"WHF Guest", b'\x8a\xdc\x96_*\xde', 11, -62, 0, False],
        [b"whfiot", b'\x9a\xdc\x96_*\xde', 11, -62, 3, False],
        [b"WHF Blue", b't\x83\xc2\xd3T@', 1, -68, 3, False],
        [b"whfiot", b'v\x83\xc2\xa3T@', 1, -68, 3, False],
        [b"WHF Guest", b'v\x83\xc2\x93T@', 1, -69, 0, False],
        [b"WHF Blue", b'\xb4\xfb\xe4\x918%', 6, -69, 3, False],
        [b"WHF Guest", b'\xba\xfb\xe4\x918%', 6, -70, 0, False],
        [b"whfiot", b'\xbe\xfb\xe4\x918%', 6, -70, 3, False],
    ]
    for result in results:
        result[0] = result[0].decode()
        result[1] = hexlify(result[1], ":").decode()
    return 200, {}, dumps(results)


def main():
    http_server = HTTPServer("localhost:4000", {
        "/": lambda p, q, h: file_view("/index.html", q, h),
        "/id": get_mac_address,
        "/scan": scan,
    }, ("", 4000))

    try:
        http_server.start()
        while True:
            pass
    except:
        http_server.stop()


if __name__ == "__main__":
    main()
