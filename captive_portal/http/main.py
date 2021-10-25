# from json import dumps
from time import sleep

from .server import HTTPServer
from .views import file_view


def get_mac_address(p, q, h):
    sleep(1)
    return 200, {}, "4c:11:ae:db:d5:a8"


def scan(p, q, h):
    sleep(2)
    # results = [
    #     ["WHF Blue", "ˆÜ–_*Þ", 11, -62, 3, False],
    #     ["WHF Guest", "ŠÜ–_*Þ", 11, -62, 0, False],
    #     ["whfiot", "šÜ–_*Þ", 11, -62, 3, False],
    #     ["WHF Blue", "tƒÂÓT@", 1, -68, 3, False],
    #     ["whfiot", "vƒÂ£T@", 1, -68, 3, False],
    #     ["WHF Guest", "vƒÂ“T@", 1, -69, 0, False],
    #     ["WHF Blue", "´ûä‘8%", 6, -69, 3, False],
    #     ["WHF Guest", "ºûä‘8%", 6, -70, 0, False],
    #     ["whfiot", "¾ûä‘8%", 6, -70, 3, False],
    # ]
    # return 200, {}, dumps(results)
    return 200, {}, """[["WHF Blue", "Ü_*Þ", 11, -66, 3, false], ["whfiot", "Ü_*Þ", 11, -66, 3, false], ["WHF Guest", "Ü_*Þ", 11, -67, 0, false], ["WHF Guest", "vÂT@", 1, -69, 0, false], ["whfiot", "vÂ£T@", 1, -69, 3, false], ["WHF Blue", "tÂÓT@", 1, -69, 3, false], ["WHF Blue", "´ûä8%", 6, -70, 3, false], ["WHF Guest", "ºûä8%", 6, -70, 0, false], ["whfiot", "¾ûä8%", 6, -71, 3, false]]"""


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
