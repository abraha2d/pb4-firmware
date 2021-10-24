from captive_portal.http.views import file_view

from utils import do_scan


def connect(path, query_dict, headers):
    if query_dict.get("ssid") is None:
        return 400, "SSID is required!"
    return 200, {}, f'SSID: {query_dict["ssid"]}\nPassword: {query_dict.get("pass")}'


def index(path, query_dict, headers):
    # networks = do_scan()
    # for ssid, aps in networks.items():
    #     print(f"SSID: {ssid}")
    #     for ap in aps:
    #         print(f"  {ap}")
    return file_view("/index.html", query_dict, headers)


def scan(path, query_dict, headers):
    networks = do_scan()
    for ssid, aps in networks.items():
        print(f"SSID: {ssid}")
        for ap in aps:
            print(f"  {ap}")
    return 200, {}, f'{networks}'
