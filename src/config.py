from upy_platform import nvs
from utils import get_device_mac


MQTT_DEVICE_BASE = f"/pb4/devices/{get_device_mac()}"

MQTT_TOPIC_STATUS = f"{MQTT_DEVICE_BASE}/status"
MQTT_TOPIC_VERSION = f"{MQTT_DEVICE_BASE}/version"

MQTT_TOPIC_OTA_FW_DATA = f"{MQTT_DEVICE_BASE}/ota/fw/data"
MQTT_TOPIC_OTA_FW_HASH = f"{MQTT_DEVICE_BASE}/ota/fw/sha256"
MQTT_TOPIC_OTA_FW_OK = f"{MQTT_DEVICE_BASE}/ota/fw/ok"

MQTT_TOPIC_OTA_APP_DATA = f"{MQTT_DEVICE_BASE}/ota/app/data"
MQTT_TOPIC_OTA_APP_HASH = f"{MQTT_DEVICE_BASE}/ota/app/sha256"
MQTT_TOPIC_OTA_APP_OK = f"{MQTT_DEVICE_BASE}/ota/app/ok"


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
