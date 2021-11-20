from binascii import hexlify
from json import dumps
from time import time

from captive_portal.http.views import file_view
from config import set_wlan_config
from upy_platform import wlan_sta, status
from utils import get_device_name


def connect(path, query_dict, headers):
    if query_dict.get("ssid") is None:
        return 400, "SSID is required!"

    ssid = query_dict["ssid"]
    password = query_dict.get("password")

    print(f"views.connect: Connecting to {ssid}/{password} ...")
    wlan_sta.config(dhcp_hostname=get_device_name())
    wlan_sta.connect(ssid, password)

    status.network_state = status.NETWORK_SCANNING

    start_time = time()
    while not wlan_sta.isconnected() and time() - start_time < 30:
        pass

    if wlan_sta.isconnected():
        print(f"views.connect: Connected.")
        set_wlan_config(ssid, password)
    else:
        print(f"views.connect: Timed out.")
        status.network_state = status.NETWORK_HOTSPOT

    return 303, {"Location": "/"}, ""


def get_mac_address(path, query_dict, headers):
    return 200, {}, hexlify(wlan_sta.config("mac"), ":")


def index(path, query_dict, headers):
    return file_view("/index.html", query_dict, headers)


def scan(path, query_dict, headers):
    print("views.scan: Scanning...")
    wlan_sta.disconnect()
    networks = wlan_sta.scan()
    networks = [network[:1] + (hexlify(network[1], ":"),) + network[2:] for network in networks]
    return 200, {}, dumps(networks)


urlconf = {
    "/": index,
    "/connect": connect,
    "/id": get_mac_address,
    "/scan": scan,
}
