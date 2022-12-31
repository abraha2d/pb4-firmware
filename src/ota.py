from binascii import hexlify
from hashlib import sha256
from math import ceil
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
    get_vfs_config,
    set_vfs_config,
)
from upy_platform import status

STAGING = Partition.find(Partition.TYPE_DATA, label="staging")[0]
BLOCK_SIZE = STAGING.ioctl(5, None)
STAGING_OFFSET = 0


async def setup_ota_subscriptions(client):
    await client.subscribe(
        (MQTT_TOPIC_OTA_FW_DATA, 2, recv_data),
        (MQTT_TOPIC_OTA_FW_HASH, 2, recv_fw_hash),
        (MQTT_TOPIC_OTA_APP_DATA, 2, recv_data),
        (MQTT_TOPIC_OTA_APP_HASH, 2, recv_app_hash),
    )


# noinspection PyUnusedLocal
async def recv_data(client, topic, data, retained):
    global STAGING_OFFSET
    if retained:
        return

    STAGING.writeblocks(STAGING_OFFSET, data)
    STAGING_OFFSET += ceil(len(data) / BLOCK_SIZE)

    print(
        f"ota.recv_data: Received {ceil(STAGING_OFFSET * BLOCK_SIZE / 1024)}K bytes"
        + f" (+{ceil(len(data) / 1024)}K)."
    )
    status.app_state = status.APP_UPGRADING


async def recv_hash(client, data, retained, to_update, ok_topic, use_ota=False):
    global STAGING_OFFSET
    if retained:
        return

    hasher = sha256()
    ota_chunk = bytearray(BLOCK_SIZE)
    for i in range(STAGING_OFFSET):
        await sleep_ms(0)
        STAGING.readblocks(i, ota_chunk)
        hasher.update(ota_chunk)
    ota_hash = hasher.digest()

    if ota_hash == data:
        print(f"ota.recv_hash: Validated hash: SHA256:{hexlify(ota_hash).decode()}")
        part_label = to_update.info()[4]

        try:
            print(f"ota.recv_hash: Writing update to partition '{part_label}'...")
            print(f"ota.recv_hash: INFO {STAGING_OFFSET}*{BLOCK_SIZE} bytes")

            if use_ota:
                handle = to_update.ota_begin(STAGING_OFFSET * BLOCK_SIZE)

            for i in range(STAGING_OFFSET):
                await sleep_ms(0)
                STAGING.readblocks(i, ota_chunk)
                if use_ota:
                    # noinspection PyUnboundLocalVariable
                    to_update.ota_write(handle, ota_chunk)
                else:
                    to_update.writeblocks(i, ota_chunk)

            print(f"ota.recv_hash: Success. Choosing '{part_label}' for next boot...")
            if use_ota:
                to_update.ota_end(handle)
                to_update.set_boot()
            else:
                set_vfs_config(part_label)

            print(f"ota.recv_hash: Done. Communicating status to broker...")
            await client.publish(ok_topic, "1", 1)

            print(f"ota.recv_hash: OK. Rebooting in 5 seconds...")
            status.app_state = status.APP_SHUTDOWN
            await sleep_ms(5000)
            status.write(status.BLACK)
            reset()
            return
        except OSError as e:  # TODO: Cast a smaller net
            print_exception(e)
    else:
        print(
            f"ota.recv_hash: Hash invalid! "
            + f"actual (SHA256:{hexlify(ota_hash).decode()}) != "
              +f"expected (SHA256:{hexlify(data).decode()})"
        )

    print(f"ota.recv_hash: Communicating failure to broker...")
    await client.publish(ok_topic, "0", 1)
    STAGING_OFFSET = 0
    status.app_state = status.APP_ERROR


async def recv_fw_hash(client, topic, data, retained):
    assert topic == MQTT_TOPIC_OTA_FW_HASH
    to_update = Partition(Partition.RUNNING).get_next_update()
    ok_topic = MQTT_TOPIC_OTA_FW_OK
    await recv_hash(client, data, retained, to_update, ok_topic, use_ota=True)


async def recv_app_hash(client, topic, data, retained):
    assert topic == MQTT_TOPIC_OTA_APP_HASH
    to_update = Partition.find(
        Partition.TYPE_DATA,
        label="app_1" if get_vfs_config() == "app_0" else "app_0",
    )[0]
    ok_topic = MQTT_TOPIC_OTA_APP_OK
    await recv_hash(client, data, retained, to_update, ok_topic)
