from binascii import hexlify
from json import dumps

from captive_portal.http.views import file_view
from config import set_wlan_config
from upy_platform import wlan_sta


def connect(path, query_dict, headers):
    if query_dict.get("ssid") is None:
        return 400, "SSID is required!"

    ssid = query_dict["ssid"]
    password = query_dict.get("password")

    wlan_sta.connect(ssid, password)
    while not wlan_sta.isconnected():
        # TODO: abort after timeout
        pass
    set_wlan_config(ssid, password)

    return 303, {"Location": "/"}, ""


def get_mac_address(path, query_dict, headers):
    return 200, {}, hexlify(wlan_sta.config("mac"), ":")


def index(path, query_dict, headers):
    return file_view("/index.html", query_dict, headers)


def scan(path, query_dict, headers):
    networks = wlan_sta.scan()
    networks = [network[:1] + (hexlify(network[1], ":"),) + network[2:] for network in networks]
    return 200, {}, dumps(networks)


urlconf = {
    "/": index,
    "/connect": connect,
    "/id": get_mac_address,
    "/scan": scan,
}
