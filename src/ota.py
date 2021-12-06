from binascii import hexlify
from hashlib import sha256
from sys import print_exception

# noinspection PyUnresolvedReferences
from esp32 import Partition
from machine import reset
from uasyncio import sleep_ms

from config import (
    MQTT_TOPIC_OTA_FW_DATA,
    MQTT_TOPIC_OTA_FW_HASH,
    MQTT_TOPIC_OTA_FW_OK,
    MQTT_TOPIC_OTA_APP_DATA,
    MQTT_TOPIC_OTA_APP_HASH,
    MQTT_TOPIC_OTA_APP_OK,
)
from upy_platform import status

FW_DATA = bytearray()
APP_DATA = bytearray()


async def setup_ota_subscriptions(client):
    await client.subscribe(
        (MQTT_TOPIC_OTA_FW_DATA, 2, recv_fw_data),
        (MQTT_TOPIC_OTA_FW_HASH, 2, recv_fw_hash),
        (MQTT_TOPIC_OTA_APP_DATA, 2, recv_app_data),
        (MQTT_TOPIC_OTA_APP_HASH, 2, recv_app_hash),
    )


# noinspection PyUnusedLocal
async def recv_fw_data(client, topic, data, retained):
    assert topic == MQTT_TOPIC_OTA_FW_DATA
    if retained:
        return

    global FW_DATA
    FW_DATA = data

    print(f"ota.recv_fw_data: Received {len(data)} bytes.")
    status.app_state = status.APP_RUNNING


async def recv_fw_hash(client, topic, data, retained):
    assert topic == MQTT_TOPIC_OTA_FW_HASH
    if retained:
        return

    global FW_DATA
    fw_hash = sha256(FW_DATA).digest()

    if fw_hash == data:
        print(f"ota.recv_fw_hash: Validated hash: SHA256:{hexlify(fw_hash)}")

        to_update = Partition(Partition.RUNNING).get_next_update()
        part_label = to_update.info()[4]

        try:
            print(f"ota.recv_fw_hash: Writing update to partition '{part_label}'...")
            handle = to_update.ota_begin(len(FW_DATA))
            to_update.ota_write(handle, FW_DATA)  # TODO: This blocks like crazy
            to_update.ota_end(handle)

            print(f"ota.recv_fw_hash: Success. Choosing '{part_label}' for next boot...")
            to_update.set_boot()

            print(f"ota.recv_fw_hash: Done. Communicating status to broker...")
            await client.publish(MQTT_TOPIC_OTA_FW_OK, "1", 1)
            status.app_state = status.APP_IDLE

            print(f"ota.recv_fw_hash: OK. Rebooting in 5 seconds...")
            await sleep_ms(5000)
            reset()
            return
        except OSError as e:
            print_exception(e)
    else:
        print(f"ota.recv_fw_hash: Hash invalid! " +
              f"actual (SHA256:{hexlify(fw_hash)}) != expected (SHA256:{hexlify(data)})")

    print(f"ota.recv_fw_hash: Communicating failure to broker...")
    await client.publish(MQTT_TOPIC_OTA_FW_OK, "0", 1)
    status.app_state = status.APP_ERROR


# noinspection PyUnusedLocal
async def recv_app_data(client, topic, data, retained):
    assert topic == MQTT_TOPIC_OTA_APP_DATA
    if retained:
        return

    APP_DATA.extend(data)
    print(f"ota.recv_app_data: Received {len(data)} bytes ({len(APP_DATA)} bytes total).")
    status.app_state = status.APP_RUNNING


async def recv_app_hash(client, topic, data, retained):
    assert topic == MQTT_TOPIC_OTA_APP_HASH
    if retained:
        return

    global APP_DATA
    app_hash = sha256(APP_DATA).digest()

    if app_hash == data:
        print(f"ota.recv_app_hash: Hash valid. OTA update not implemented.")
        await client.publish(MQTT_TOPIC_OTA_APP_OK, "1", 1)
        status.app_state = status.APP_IDLE
    else:
        print(f"ota.recv_app_hash: Hash invalid! " +
              f"actual ({hexlify(app_hash)}) != expected ({hexlify(data)})")
        await client.publish(MQTT_TOPIC_OTA_APP_OK, "0", 1)
        APP_DATA = bytearray()
        status.app_state = status.APP_ERROR
