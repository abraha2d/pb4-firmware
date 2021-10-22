print("===IMPORTING views.py===")
from captive_portal.http.views import template

from utils import do_scan


def connect(uri, qps, headers):
    if qps.get("ssid") is None:
        return 400, "SSID is required!"
    return 200, {}, f'SSID: {qps["ssid"]}\nPassword: {qps.get("pass")}'


def index(uri, qps, headers):
    networks = do_scan()
    for ssid, aps in networks.items():
        print(f"SSID: {ssid}")
        for ap in aps:
            print(f"  {ap}")
    return template("/index.html", qps, headers)
