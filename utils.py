print("===IMPORTING utils.py===")
from platform import wlan_sta


def do_scan():
    network_list = wlan_sta.scan()
    networks = {}
    for network_info in network_list:
        ssid, bssid, channel, rssi, authmode, hidden = network_info
        if hidden:
            continue
        networks.setdefault((ssid, authmode), []).append({
            "bssid": bssid,
            "channel": channel,
            "rssi": rssi,
        })
    return networks
