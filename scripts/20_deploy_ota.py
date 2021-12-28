from binascii import hexlify
from hashlib import sha256
from sys import argv

import paho.mqtt.client as mqtt

DATA_TOPIC = "/pb4/devices/{}/ota/{}/data"
HASH_TOPIC = "/pb4/devices/{}/ota/{}/sha256"
OK_TOPIC = "/pb4/devices/{}/ota/{}/ok"

OTA_TYPE = None
OTA_DEVICE = None

OTA_DATA = None
OTA_HASH = None


# noinspection PyUnusedLocal
def on_connect(client, userdata, flags, rc):
    global OTA_DATA

    client.on_connect = None
    print(" connected.")
    print("Publishing data...", end="", flush=True)
    client.publish(DATA_TOPIC.format(OTA_DEVICE, OTA_TYPE), OTA_DATA, qos=2)
    OTA_DATA = None


# noinspection PyUnusedLocal
def on_publish(client, userdata, mid):
    global OTA_HASH

    if OTA_HASH is not None:
        print(" done.")
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
    global OTA_DATA, OTA_DEVICE, OTA_HASH, OTA_TYPE

    OTA_TYPE = argv[1]
    OTA_DEVICE = argv[2]

    bin_file = f"build/{OTA_TYPE}.bin"

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    print(f"Reading {bin_file}...", end="", flush=True)
    with open(bin_file, "rb") as payload_file:
        OTA_DATA = payload_file.read()
        print(f" done. {len(OTA_DATA)} bytes.")

        print("Hashing...", end="", flush=True)
        OTA_HASH = sha256(OTA_DATA).digest()
        print(" done.")
        print(f"SHA256: {hexlify(OTA_HASH).decode()}")

    print("Connecting to MQTT broker...", end="", flush=True)
    client.connect("pb4_control.local", keepalive=1)
    client.loop_forever()


if __name__ == "__main__":
    main()
