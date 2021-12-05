import micropython

micropython.alloc_emergency_exception_buf(100)

from os import uname

from machine import reset

from captive_portal.dns.server import DNSServer
from captive_portal.http.server import HTTPServer
from mqtt.client import MQTTClient

from config import (
    MQTT_SERVER,
    MQTT_TOPIC_STATUS,
    MQTT_TOPIC_VERSION,
    erase_wlan_config,
    get_wlan_config,
)
from ota import setup_ota_subscriptions
from upy_platform import boot, status, wlan_ap, wlan_sta
from utils import get_device_mac, get_device_name, connect_wlan
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

    status.network_state = status.NETWORK_HOTSPOT
    while not wlan_sta.isconnected():
        pass

    print("main.do_setup: Stopping hotspot...")
    http_server.stop()
    dns_server.stop()
    wlan_ap.active(False)


def do_connect():
    wlan_config = get_wlan_config()

    if wlan_config is not None:
        wlan_ssid, wlan_pass = wlan_config
        connect_wlan(wlan_ssid, wlan_pass)
    else:
        print("main.do_connect: No config.")

    if not wlan_sta.isconnected():
        do_setup()


def do_reset():
    erase_wlan_config()


def main():
    print("main.main: Booting... hold BOOT while the LED is magenta to factory reset.")
    status.app_state = status.APP_BOOTING
    await sleep_ms(1000)

    if boot.value():
        print("main.main: Resetting...")
        status.app_state = status.APP_RESETTING
        do_reset()
        print("main.main: Rebooting...")
        reset()

    do_connect()

    status_offline = [MQTT_TOPIC_STATUS, "0", 1, True]
    status_online = [MQTT_TOPIC_STATUS, "1", 1, True]

    mqtt_client = MQTTClient(
        server=MQTT_SERVER,
        client_id=get_device_mac(),
        lwt=status_offline,
        keepalive=10,
    )

    mqtt_client.publish(*status_online)
    mqtt_client.publish(MQTT_TOPIC_VERSION, uname().version, 1, True)

    setup_ota_subscriptions(mqtt_client)

    status.app_state = status.APP_IDLE


if __name__ == '__main__':
    main()
