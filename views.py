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


def index(path, query_dict, headers):
    return file_view("/index.html", query_dict, headers)


def scan(path, query_dict, headers):
    networks = wlan_sta.scan()
    return 200, {}, dumps(networks)


urlconf = {
    "/": index,
    "/connect": connect,
    "/scan": scan,
}
