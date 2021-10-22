from platform import nvs


def get_wlan_config():
    try:
        wlan_ssid_len = nvs.get_i32("wlan_ssid_len")
        wlan_ssid = bytearray(wlan_ssid_len)
        assert nvs.get_blob("wlan_ssid", wlan_ssid) == wlan_ssid_len
        wlan_pass_len = nvs.get_i32("wlan_pass_len")
        wlan_pass = bytearray(wlan_pass_len)
        assert nvs.get_blob("wlan_pass", wlan_pass) == wlan_pass_len
        return wlan_ssid.decode(), wlan_pass.decode()
    except (OSError, AssertionError):
        return False


def set_wlan_config(wlan_ssid, wlan_pass):
    nvs.set_blob("wlan_ssid", wlan_ssid)
    nvs.set_i32("wlan_ssid_len", len(wlan_ssid))
    nvs.set_blob("wlan_pass", wlan_pass)
    nvs.set_i32("wlan_pass_len", len(wlan_pass))
    nvs.commit()


def erase_wlan_config():
    nvs.erase_key("wlan_ssid")
    nvs.erase_key("wlan_ssid_len")
    nvs.erase_key("wlan_pass")
    nvs.erase_key("wlan_pass_len")
