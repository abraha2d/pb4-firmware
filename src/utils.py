from binascii import hexlify

from utime import time

from upy_platform import status, wlan_sta


def get_device_mac():
    return hexlify(wlan_sta.config('mac'))[-6:].decode()


def get_device_name():
    mac = get_device_mac()
    return f"pb4_{mac}"


def connect_wlan(ssid, password, timeout=30):
    print(f"utils.connect_wlan: Connecting to {ssid} / {password} ...")
    status.network_state = status.NETWORK_SCANNING

    wlan_sta.active(True)
    wlan_sta.config(dhcp_hostname=get_device_name())
    wlan_sta.connect(ssid, password)

    start_time = time()
    while not wlan_sta.isconnected() and time() - start_time < timeout:
        pass

    if wlan_sta.isconnected():
        print(f"utils.connect_wlan: Connected. Network config: {wlan_sta.ifconfig()}")
        status.network_state = status.NETWORK_CONNECTED
    else:
        print(f"utils.connect_wlan: Timed out.")
        status.network_state = None
