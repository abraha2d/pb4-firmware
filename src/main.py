from errno import EPERM
from os import uname

# noinspection PyUnresolvedReferences
from esp32 import Partition
from machine import reset
from uasyncio import create_task, get_event_loop, run, sleep_ms

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
from utils import get_device_mac, get_device_name, connect_wlan, wlan_is_connected
from views import urlconf


async def do_setup():
    print("main.do_setup: Starting hotspot...")
    wlan_ap.active(True)

    device_name = get_device_name()
    wlan_ap.config(
        dhcp_hostname=device_name,
        essid=device_name.upper(),
    )

    ip_address = wlan_ap.ifconfig()[0]
    dns_task = create_task(DNSServer(ip_address).serve())
    http_task = create_task(HTTPServer(ip_address, urlconf).serve())

    print("main.do_setup: Waiting for configuration...")
    status.network_state = status.NETWORK_HOTSPOT
    await wlan_is_connected()

    print("main.do_setup: Stopping hotspot...")
    wlan_ap.active(False)
    dns_task.cancel()
    http_task.cancel()


async def do_connect():
    wlan_config = get_wlan_config()

    if wlan_config is not None:
        wlan_ssid, wlan_pass = wlan_config
        await connect_wlan(wlan_ssid, wlan_pass)
    else:
        print("main.do_connect: No configuration.")

    if not wlan_sta.isconnected():
        await do_setup()


def do_reset():
    erase_wlan_config()


async def main():
    print("main.main: Booting... hold BOOT within the next second to factory reset.")
    status.app_state = status.APP_BOOTING
    await sleep_ms(1000)

    if boot.value():
        print("main.main: Performing factory reset...")
        status.app_state = status.APP_RESETTING
        do_reset()
        print("main.main: Rebooting...")
        reset()

    await do_connect()

    print("main.main: Starting MQTT client...")
    status_offline = [MQTT_TOPIC_STATUS, "0", 1, True]
    status_online = [MQTT_TOPIC_STATUS, "1", 1, True]

    mqtt_client = MQTTClient(
        server=MQTT_SERVER,
        client_id=get_device_mac(),
        lwt=status_offline,
        keepalive=10,
    )

    create_task(mqtt_client.run())

    await mqtt_client.publish(*status_online)
    await mqtt_client.publish(MQTT_TOPIC_VERSION, uname().version, 1, True)

    await setup_ota_subscriptions(mqtt_client)

    status.app_state = status.APP_IDLE

    # TODO: try to run as much initialization as possible before calling this
    if Partition(Partition.RUNNING).info()[4] != "factory":
        Partition.mark_app_valid_cancel_rollback()

    loop = get_event_loop()
    loop.run_forever()


if __name__ == '__main__':
    run(main())
