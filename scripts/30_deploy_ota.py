#!/usr/bin/env python3

from binascii import hexlify
from hashlib import sha256
from math import ceil
from sys import argv

import paho.mqtt.client as mqtt

DATA_TOPIC = "/pb4/devices/{}/ota/{}/data"
HASH_TOPIC = "/pb4/devices/{}/ota/{}/sha256"
OK_TOPIC = "/pb4/devices/{}/ota/{}/ok"

OTA_TYPE = None
OTA_DEVICE = None

BLOCK_SIZE = 4096  # hard to get from target device without a lot of work
CHUNK_SIZE = 65536  # max 66977
OTA_CHUNKS = None
OTA_HASH = None


def progress():
    while True:
        yield from "-\\|/"


PROGRESS = progress()


# noinspection PyUnusedLocal
def on_connect(client, userdata, flags, rc):
    client.on_connect = None
    print(" connected.")
    print("Publishing data...  ", end="", flush=True)
    on_publish(client, None, None)


# noinspection PyUnusedLocal
def on_publish(client, userdata, mid):
    global OTA_CHUNKS, OTA_HASH

    if len(OTA_CHUNKS) > 0:
        print(f"\b{next(PROGRESS)}", end="", flush=True)
        client.publish(DATA_TOPIC.format(OTA_DEVICE, OTA_TYPE), OTA_CHUNKS[0], qos=2)
        OTA_CHUNKS = OTA_CHUNKS[1:]
    elif OTA_HASH is not None:
        print("\bdone.")
        print("Publishing hash...", end="", flush=True)
        client.publish(HASH_TOPIC.format(OTA_DEVICE, OTA_TYPE), OTA_HASH, qos=2)
        OTA_HASH = None
    else:
        print(" done.")
        print("Subscribing...", end="", flush=True)
        client.subscribe(OK_TOPIC.format(OTA_DEVICE, OTA_TYPE), qos=1)


# noinspection PyUnusedLocal
def on_subscribe(client, userdata, mid, granted_qos):
    print(" done.")
    print("Waiting for OK...", end="", flush=True)


# noinspection PyUnusedLocal
def on_message(client, userdata, message):
    if message.payload == b"1":
        print(" OK.")
        client.disconnect()
    else:
        print(" not OK!")
        client.disconnect()


def main():
    global CHUNK_SIZE, OTA_CHUNKS, OTA_DEVICE, OTA_HASH, OTA_TYPE

    OTA_TYPE = argv[1]
    OTA_DEVICE = argv[2]

    bin_file = f"build/{'micropython' if OTA_TYPE == 'fw' else OTA_TYPE}.bin"

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    print(f"Reading {bin_file}...", end="", flush=True)
    with open(bin_file, "rb") as payload_file:
        raw_data = payload_file.read()
        print(f" done. {len(raw_data)} bytes.")

        print(
            f"Extending to nearest {ceil(BLOCK_SIZE / 1024)}K block...",
            end="",
            flush=True,
        )
        pad_length = ceil(len(raw_data) / BLOCK_SIZE) * BLOCK_SIZE
        ota_data = raw_data.ljust(pad_length, b"\xFF")
        print(f" done. {ceil(pad_length / 1024)}K bytes.")

        print("Hashing...", end="", flush=True)
        OTA_HASH = sha256(ota_data).digest()
        print(" done.")
        print(f"SHA256: {hexlify(OTA_HASH).decode()}")

        print("Chunking...", end="", flush=True)
        OTA_CHUNKS = [
            ota_data[i : i + CHUNK_SIZE] for i in range(0, len(ota_data), CHUNK_SIZE)
        ]
        print(" done.")
        print(
            f"{len(OTA_CHUNKS)} chunks. "
            + f"Max chunk size: {ceil(CHUNK_SIZE / 1024)}K bytes."
        )

    print("Connecting to MQTT broker...", end="", flush=True)
    client.connect("pb4_control.local", keepalive=1)
    client.loop_forever()


if __name__ == "__main__":
    main()
