from io import StringIO
from os import uname

# noinspection PyUnresolvedReferences
from esp32 import Partition
from machine import reset
from sys import print_exception
from uasyncio import create_task, get_event_loop, run, sleep_ms

from captive_portal.dns.server import DNSServer
from captive_portal.http.server import HTTPServer
from mqtt.client import MQTTClient

from config import (
    MQTT_SERVER,
    MQTT_TOPIC_ERRORS,
    MQTT_TOPIC_STATUS,
    MQTT_TOPIC_FW_VER,
    MQTT_TOPIC_APP_NAME,
    MQTT_TOPIC_APP_VER,
    erase_vfs_config,
    erase_wlan_config,
    get_wlan_config,
)
from drivers import DRIVER_LIST, handle_i2c
from ota import setup_ota_subscriptions
from upy_platform import boot, status, version, wlan_ap, wlan_sta
from utils import get_device_mac, get_device_name, connect_wlan, wlan_is_connected

# noinspection PyUnresolvedReferences
from version import NAME as APP_NAME, VERSION as APP_VERSION
from views import urlconf

mqtt_client = None


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
    status.network_state = status.NETWORK_CONNECTED

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
    erase_vfs_config()
    erase_wlan_config()


def exc_handler(loop, context):
    status.app_state = status.APP_ERROR

    if mqtt_client is not None:
        sio = StringIO()
        print_exception(context["exception"], sio)
        traceback = sio.getvalue()
        create_task(
            mqtt_client.publish(
                MQTT_TOPIC_ERRORS,
                traceback,
                qos=2,
                retain=True,
            )
        )

    return loop.default_exception_handler(loop, context)


async def main():
    global mqtt_client

    loop = get_event_loop()
    loop.set_exception_handler(exc_handler)

    print("main.main: Hold BOOT within the next second to factory reset...")
    status.app_state = status.APP_BOOTING

    create_task(status.run())
    await sleep_ms(1000)

    if boot.value():
        print("main.main: Performing factory reset...")
        status.app_state = status.APP_RESETTING
        do_reset()
        print("main.main: Done. Rebooting in 5 seconds...")
        await sleep_ms(5000)
        status.write(status.BLACK)
        reset()

    if version == 2:
        print(
            "main.main: PB 2.0 has Wi-Fi issues. "
            + "Not starting network-connected features..."
        )
    else:
        create_task(do_connect())

        print("main.main: Starting MQTT client...")
        status_offline = [MQTT_TOPIC_STATUS, "0", 1, True]
        status_online = [MQTT_TOPIC_STATUS, "1", 1, True]

        mqtt_client = MQTTClient(
            server=MQTT_SERVER,
            client_id=get_device_mac(),
            lwt=status_offline,
            bc=status_online,
            keepalive=10,
        )

        create_task(mqtt_client.run())
        create_task(mqtt_client.publish(MQTT_TOPIC_FW_VER, uname().version, 1, True))
        create_task(mqtt_client.publish(MQTT_TOPIC_APP_NAME, APP_NAME, 1, True))
        create_task(mqtt_client.publish(MQTT_TOPIC_APP_VER, f"v{APP_VERSION}", 1, True))
        create_task(setup_ota_subscriptions(mqtt_client))

    status.app_state = status.APP_IDLE

    driver_config = []
    app_config = []

    if version == 2:
        print("main.main: Note: MQTT not available, using hardcoded configuration.")
        app_config.append("whcontrol")
    else:
        # TODO: get config from MQTT
        app_config.append("watchdog")
        app_config.append("webrepl")

        if get_device_mac() in [
            "dbcd50",  # S/N 001 DUO, 1S
            "dbd5d8",  # S/N 002 UNO, 2E
            "dbd4c4",  # S/N 004 UNO
            "dbcd68",  # S/N 005 UNO
            "dbd4bc",  # S/N 006 UNO
            "dbcd48",  # S/N 007 UNO
        ]:
            driver_config.append("vl53l1x")
            app_config.append("pb_exhaust")
            app_config.append("pb_flush")

    for driver_id in driver_config:
        try:
            driver = getattr(__import__(f"drivers.{driver_id}"), driver_id)
            driver_name = getattr(driver, "NAME", driver_id)
            print(f"main.main: Registering driver '{driver_name}'...")
            driver.register()
        except ImportError:
            print(f"main.main: Skipping unknown driver ID '{driver_id}'...")
        except AttributeError:
            print(f"main.main: Skipping broken driver '{driver_id}'")

    if DRIVER_LIST:
        print(f"main.main: Starting I2C handler...")
        create_task(handle_i2c())

    for app_id in app_config:
        try:
            app = getattr(__import__(f"apps.{app_id}"), app_id)
            app_name = getattr(app, "NAME", app_id)
            print(f"main.main: Starting app '{app_name}'...")
            create_task(app.main(mqtt_client))
        except ImportError:
            print(f"main.main: Skipping unknown app ID '{app_id}'...")
        except AttributeError:
            print(f"main.main: Skipping broken app '{app_id}'")

    # TODO: try to run as much initialization as possible before calling this
    if Partition(Partition.RUNNING).info()[4] != "factory":
        Partition.mark_app_valid_cancel_rollback()

    print("main.main: Handing control to event loop...")
    loop.run_forever()


if __name__ == "__main__":
    run(main())
