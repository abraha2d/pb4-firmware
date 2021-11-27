from hashlib import sha256
from os import uname

import micropython; micropython.alloc_emergency_exception_buf(100)
from machine import reset
from utime import sleep_ms, time

from captive_portal.dns.server import DNSServer
from captive_portal.http.server import HTTPServer
from mqtt.client import MQTTClient

from config import (
    MQTT_TOPIC_STATUS,
    MQTT_TOPIC_VERSION,
    MQTT_TOPIC_OTA_FW_DATA,
    MQTT_TOPIC_OTA_FW_HASH,
    MQTT_TOPIC_OTA_APP_DATA,
    MQTT_TOPIC_OTA_APP_HASH,
    erase_wlan_config,
    get_wlan_config, MQTT_TOPIC_OTA_FW_OK, MQTT_TOPIC_OTA_APP_OK,
)
from upy_platform import boot, status, wlan_ap, wlan_sta
from utils import get_device_name
from views import urlconf


def do_setup():
    print("main.do_setup: Starting hotspot...")
    wlan_ap.active(True)

    device_name = get_device_name()
    wlan_ap.config(
        dhcp_hostname=device_name,
        essid=device_name.upper(),
    )

    ip_address = wlan_ap.ifconfig()[0]
    dns_server = DNSServer(ip_address)
    http_server = HTTPServer(ip_address, urlconf)

    dns_server.start()
    http_server.start()

    status.network_state = status.NETWORK_HOTSPOT
    while not wlan_sta.isconnected():
        pass

    print("main.do_setup: Stopping hotspot...")
    dns_server.stop()
    http_server.stop()
    wlan_ap.active(False)


def do_connect():
    wlan_sta.active(True)
    wlan_config = get_wlan_config()

    if not wlan_config:
        print("main.do_connect: No config.")
        do_setup()
    else:
        wlan_ssid, wlan_pass = wlan_config
        print(f"main.do_connect: Connecting to {wlan_ssid} / {wlan_pass} ...")

        wlan_sta.config(dhcp_hostname=get_device_name())
        wlan_sta.connect(wlan_ssid, wlan_pass)

        status.network_state = status.NETWORK_SCANNING

        start_time = time()
        while not wlan_sta.isconnected() and time() - start_time < 30:
            pass

        if not wlan_sta.isconnected():
            print(f"main.do_connect: Timed out.")
            do_setup()

    print(f"main.do_connect: Connected. Network config: {wlan_sta.ifconfig()}")
    status.network_state = status.NETWORK_CONNECTED


def do_reset():
    erase_wlan_config()


FW_DATA = bytearray()
APP_DATA = bytearray()


def recv_ota_fw_data(client, topic, data, qos, retain):
    assert topic == MQTT_TOPIC_OTA_FW_DATA
    FW_DATA.extend(data)
    print(f"main.recv_ota_fw_data: Received {len(data)} bytes ({len(FW_DATA)} bytes total).")
    status.app_state = status.APP_RUNNING


def recv_ota_fw_hash(client, topic, data, qos, retain):
    assert topic == MQTT_TOPIC_OTA_FW_HASH

    global FW_DATA
    fw_hash = sha256(FW_DATA).digest()

    if fw_hash == data:
        print(f"main.recv_ota_fw_hash: Hash valid. OTA update not implemented.")
        client.publish(MQTT_TOPIC_OTA_FW_OK, "1", 1)
        status.app_state = status.APP_IDLE
    else:
        print(f"main.recv_ota_fw_hash: Hash invalid! " +
              f"actual (SHA256:{fw_hash.decode()}) != expected (SHA256:{data.decode()})")
        client.publish(MQTT_TOPIC_OTA_FW_OK, "0", 1)
        FW_DATA = bytearray()
        status.app_state = status.APP_IDLE


def recv_ota_app_data(client, topic, data, qos, retain):
    assert topic == MQTT_TOPIC_OTA_APP_DATA
    APP_DATA.extend(data)
    print(f"main.recv_ota_app_data: Received {len(data)} bytes ({len(APP_DATA)} bytes total).")
    status.app_state = status.APP_RUNNING


def recv_ota_app_hash(client, topic, data, qos, retain):
    assert topic == MQTT_TOPIC_OTA_APP_HASH

    global APP_DATA
    app_hash = sha256(APP_DATA).digest()

    if app_hash == data:
        print(f"main.recv_ota_app_hash: Hash valid. OTA update not implemented.")
        client.publish(MQTT_TOPIC_OTA_APP_OK, "1", 1)
        status.app_state = status.APP_IDLE
    else:
        print(f"main.recv_ota_app_hash: Hash invalid! " +
              f"actual ({app_hash}) != expected ({data})")
        client.publish(MQTT_TOPIC_OTA_APP_OK, "0", 1)
        APP_DATA = bytearray()
        status.app_state = status.APP_ERROR


mqtt_client = None

def main():
    global mqtt_client
    print("main.main: Booting... press BOOT within the next second to factory reset.")
    status.app_state = status.APP_BOOTING
    sleep_ms(1000)

    if boot.value():
        print("main.main: Resetting...")
        status.app_state = status.APP_RESETTING
        sleep_ms(2000)
        do_reset()
        print("main.main: Rebooting...")
        sleep_ms(1000)
        reset()

    do_connect()

    status_offline = [MQTT_TOPIC_STATUS, "0", 1, True]
    status_online = [MQTT_TOPIC_STATUS, "1", 1, True]

    mqtt_client = MQTTClient(lwt=status_offline, keepalive=10)
    mqtt_client.start()

    mqtt_client.publish(*status_online)
    mqtt_client.publish(MQTT_TOPIC_VERSION, uname().version, 1, True)

    mqtt_client.subscribe(
        (MQTT_TOPIC_OTA_FW_DATA, 2, recv_ota_fw_data),
        (MQTT_TOPIC_OTA_FW_HASH, 2, recv_ota_fw_hash),
        (MQTT_TOPIC_OTA_APP_DATA, 2, recv_ota_app_data),
        (MQTT_TOPIC_OTA_APP_HASH, 2, recv_ota_app_hash),
    )

    status.app_state = status.APP_IDLE


if __name__ == '__main__':
    main()
