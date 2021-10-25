from json import dumps
from time import sleep

from .server import HTTPServer
from .views import file_view


def get_mac_address(p, q, h):
    return 200, {}, "4c:11:ae:db:d5:a9"


def scan(p, q, h):
    sleep(5)
    results = [
        ('WHF Guest', b'\x8a\xdc\x96_*\xde'.decode('cp1252'), 11, -66, 0, 0),
        ('WHF Guest', b'\xba\xfb\xe4\x918%'.decode('cp1252'), 6, -77, 0, 0),
        ('WHF Guest', b'v\x83\xc2\x93T@'.decode('cp1252'), 1, -79, 0, 0),
        ('WHF Blue', b'\x88\xdc\x96_*\xde'.decode('cp1252'), 11, -66, 3, 0),
        ('WHF Blue', b'\xb4\xfb\xe4\x918%'.decode('cp1252'), 6, -77, 3, 0),
        ('WHF Blue', b't\x83\xc2\xd3T@'.decode('cp1252'), 1, -79, 3, 0),
        ('whfiot', b'\x9a\xdc\x96_*\xde'.decode('cp1252'), 11, -66, 3, 0),
        ('whfiot', b'\xbe\xfb\xe4\x918%'.decode('cp1252'), 6, -77, 3, 0),
        ('whfiot', b'v\x83\xc2\xa3T@'.decode('cp1252'), 1, -79, 3, 0),
    ]
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
