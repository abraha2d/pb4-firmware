import micropython; micropython.alloc_emergency_exception_buf(100)

from captive_portal.dns.server import DNSServer
from captive_portal.http.server import HTTPServer

from config import get_wlan_config
from platform import wlan_ap, wlan_sta
from views import urlconf


def do_setup():
    wlan_ap.active(True)
    ip_address = wlan_ap.ifconfig()[0]

    dns_server = DNSServer(ip_address)
    http_server = HTTPServer(ip_address, urlconf)

    dns_server.start()
    http_server.start()

    while not wlan_sta.isconnected():
        pass

    dns_server.stop()
    http_server.stop()

    wlan_ap.active(False)


def do_connect():
    wlan_sta.active(True)
    wlan_config = get_wlan_config()

    if not wlan_config:
        do_setup()
    else:
        wlan_ssid, wlan_pass = wlan_config
        wlan_sta.connect(wlan_ssid, wlan_pass)

        while not wlan_sta.isconnected():
            # TODO: do_serve() after timeout
            pass

    print('network config:', wlan_sta.ifconfig())


def main():
    do_connect()


if __name__ == '__main__':
    main()
