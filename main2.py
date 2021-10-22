import micropython; micropython.alloc_emergency_exception_buf(100)

from captive_portal.dns.server import DNSServer
from captive_portal.http.server import HTTPServer

from config import get_wlan_config
from platform import wlan_ap, wlan_sta
from urlconf import urlconf


def do_connect():
    print("===STARTING main.do_connect()===")
    wlan_sta.active(True)
    print("===GETTING wlan config===")
    wlan_config = get_wlan_config()
    if not wlan_config:
        print("===NO CONFIG, starting AP===")
        wlan_ap.active(True)
        ip_address = wlan_ap.ifconfig()[0]
        dns_server = DNSServer(ip_address)
        http_server = HTTPServer(ip_address, urlconf)
        print("===ENTERING infinite loop===")
        while True:
            dns_server.process()
            http_server.process()
    else:
        print("===CONNECTING to Wi-Fi===")
        wlan_ssid, wlan_pass = wlan_config
        wlan_sta.connect(wlan_ssid, wlan_pass)
    while not wlan_sta.isconnected():
        # TODO: Start AP after timeout
        pass
    print("===CONNECTED to Wi-Fi===")
    print('network config:', wlan_sta.ifconfig())


def main():
    print("===STARTING main.main()===")
    do_connect()


# if __name__ == '__main__':
#     main()
