from binascii import hexlify

from uasyncio import TimeoutError, sleep_ms, wait_for

from upy_platform import status, wlan_sta


def get_device_mac():
    return hexlify(wlan_sta.config("mac"))[-6:].decode()


def get_device_name():
    mac = get_device_mac()
    return f"pb4_{mac}"


async def wlan_is_connected():
    while True:
        if wlan_sta.isconnected():
            return
        await sleep_ms(100)


async def connect_wlan(ssid, password, timeout=30):
    print(f"utils.connect_wlan: Connecting to {ssid} / {password} ...")
    status.network_state = status.NETWORK_SCANNING

    wlan_sta.active(True)
    wlan_sta.config(dhcp_hostname=get_device_name())
    wlan_sta.connect(ssid, password)

    print(f"utils.connect_wlan: Waiting a maximum of {timeout} seconds...")
    try:
        await wait_for(wlan_is_connected(), timeout)
    except TimeoutError:
        pass

    if wlan_sta.isconnected():
        print(f"utils.connect_wlan: Connected. Network config: {wlan_sta.ifconfig()}")
        status.network_state = status.NETWORK_CONNECTED
    else:
        print(f"utils.connect_wlan: Timed out.")
        status.network_state = None
