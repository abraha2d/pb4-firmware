from upy_platform import nvs
from utils import get_device_mac

MQTT_SERVER = "pb4_control.local"
MQTT_DEVICE_BASE = f"/pb4/devices/{get_device_mac()}"
MQTT_APPS_BASE = f"{MQTT_DEVICE_BASE}/apps"

MQTT_TOPIC_STATUS = f"{MQTT_DEVICE_BASE}/status"
MQTT_TOPIC_FW_VER = f"{MQTT_DEVICE_BASE}/fw_version"
MQTT_TOPIC_APP_NAME = f"{MQTT_DEVICE_BASE}/app_name"
MQTT_TOPIC_APP_VER = f"{MQTT_DEVICE_BASE}/app_version"
MQTT_TOPIC_ERRORS = f"{MQTT_DEVICE_BASE}/errors"

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
    except OSError as e:
        if e.errno == -4354:  # ESP_ERR_NVS_NOT_FOUND
            print("config.get_wlan_config: NVS not found.")
            return None
        raise
    except AssertionError:
        print("config.get_wlan_config: Malformed configuration, erasing...")
        erase_wlan_config()
        return None


def set_wlan_config(wlan_ssid, wlan_pass):
    nvs.set_blob("wlan_ssid", wlan_ssid)
    nvs.set_i32("wlan_ssid_len", len(wlan_ssid))
    nvs.set_blob("wlan_pass", wlan_pass)
    nvs.set_i32("wlan_pass_len", len(wlan_pass))
    nvs.commit()


def erase_wlan_config():
    try:
        nvs.erase_key("wlan_ssid")
        nvs.erase_key("wlan_ssid_len")
        nvs.erase_key("wlan_pass")
        nvs.erase_key("wlan_pass_len")
    except OSError as e:
        if e.errno == -4354:  # ESP_ERR_NVS_NOT_FOUND
            print("config.erase_wlan_config: NVS not found.")
            return
        raise


def get_vfs_config():
    try:
        vfs_config = nvs.get_i32("vfs_config")
        return "app_1" if vfs_config else "app_0"
    except OSError as e:
        if e.errno == -4354:  # ESP_ERR_NVS_NOT_FOUND
            print("config.get_vfs_config: NVS not found.")
            return "vfs"
        raise


def set_vfs_config(vfs_config):
    nvs.set_i32("vfs_config", vfs_config == "app_1")
    nvs.commit()


def erase_vfs_config():
    try:
        nvs.erase_key("vfs_config")
    except OSError as e:
        if e.errno == -4354:  # ESP_ERR_NVS_NOT_FOUND
            print("config.erase_vfs_config: NVS not found.")
            return
        raise
