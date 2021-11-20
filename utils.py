from binascii import hexlify
from upy_platform import wlan_sta


def get_device_name():
    mac = hexlify(wlan_sta.config('mac'))[-6:].decode()
    return f"pb4_{mac}"
