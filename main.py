import micropython; micropython.alloc_emergency_exception_buf(100)
from machine import reset
from time import sleep_ms, time

from captive_portal.dns.server import DNSServer
from captive_portal.http.server import HTTPServer

from config import erase_wlan_config, get_wlan_config
from upy_platform import boot, status, wlan_ap, wlan_sta
from utils import get_device_name
from views import urlconf


def do_setup():
    print("main.do_setup: Starting hotspot...")
    wlan_ap.active(True)

    device_name = get_device_name()
    wlan_ap.config(
        dhcp_hostname=device_name,
        essid=device_name.upper(),
    )

    ip_address = wlan_ap.ifconfig()[0]
    dns_server = DNSServer(ip_address)
    http_server = HTTPServer(ip_address, urlconf)

    dns_server.start()
    http_server.start()

    status.network_state = status.NETWORK_HOTSPOT
    while not wlan_sta.isconnected():
        pass

    print("main.do_setup: Stopping hotspot...")
    dns_server.stop()
    http_server.stop()
    wlan_ap.active(False)


def do_connect():
    wlan_sta.active(True)
    wlan_config = get_wlan_config()

    if not wlan_config:
        print("main.do_connect: No config.")
        do_setup()
    else:
        wlan_ssid, wlan_pass = wlan_config
        print(f"main.do_connect: Connecting to {wlan_ssid}/{wlan_pass} ...")

        wlan_sta.config(dhcp_hostname=get_device_name())
        wlan_sta.connect(wlan_ssid, wlan_pass)

        status.network_state = status.NETWORK_SCANNING

        start_time = time()
        while not wlan_sta.isconnected() and time() - start_time < 30:
            pass

        if not wlan_sta.isconnected():
            print(f"main.do_connect: Timed out.")
            do_setup()

    print(f"main.do_connect: Connected. Network config: {wlan_sta.ifconfig()}")
    status.network_state = status.NETWORK_CONNECTED


def do_reset():
    erase_wlan_config()


def main():
    print("main.main: Booting... press BOOT within the next second to factory reset.")
    status.app_state = status.APP_BOOTING
    sleep_ms(1000)

    if boot.value():
        print("main.main: Resetting...")
        status.app_state = status.APP_RESETTING
        sleep_ms(2000)
        do_reset()
        print("main.main: Rebooting...")
        sleep_ms(1000)
        reset()

    do_connect()

    status.app_stat = status.APP_IDLE


if __name__ == '__main__':
    main()
