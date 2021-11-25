from binascii import hexlify
from upy_platform import wlan_sta


def get_device_mac():
    return hexlify(wlan_sta.config('mac'))[-6:].decode()


def get_device_name():
    mac = get_device_mac()
    return f"pb4_{mac}"
