from binascii import hexlify
from json import dumps

from captive_portal.http.views import file_view
from config import set_wlan_config
from upy_platform import wlan_sta, status
from utils import connect_wlan


# noinspection PyUnusedLocal
async def connect(path, query_dict, headers):
    if query_dict.get("ssid") is None:
        return 400, {}, "SSID is required!"

    ssid = query_dict["ssid"]
    password = query_dict.get("password")

    await connect_wlan(ssid, password)

    if wlan_sta.isconnected():
        print(f"views.connect: Saving configuration...")
        set_wlan_config(ssid, password)
    else:
        status.network_state = status.NETWORK_HOTSPOT

    return 303, {"Location": "/"}, ""


# noinspection PyUnusedLocal
async def get_mac_address(path, query_dict, headers):
    return 200, {}, hexlify(wlan_sta.config("mac"), ":")


# noinspection PyUnusedLocal
async def index(path, query_dict, headers):
    return await file_view("/index.html", query_dict, headers)


# noinspection PyUnusedLocal
async def scan(path, query_dict, headers):
    wlan_sta.active(True)
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
