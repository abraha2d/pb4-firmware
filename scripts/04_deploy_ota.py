from binascii import hexlify
from hashlib import sha256

import paho.mqtt.client as mqtt

APP_BIN = "build/app.bin"
DEVICE_ID = "dbd5a8"

DATA_TOPIC = f"/pb4/devices/{DEVICE_ID}/ota/app/data"
HASH_TOPIC = f"/pb4/devices/{DEVICE_ID}/ota/app/sha256"
OK_TOPIC = f"/pb4/devices/{DEVICE_ID}/ota/app/ok"

MESSAGE_DATA = None
MESSAGE_HASH = None


def on_connect(client, userdata, flags, rc):
    global MESSAGE_DATA

    client.on_connect = None
    print(" connected.")
    print("Publishing data...", end="", flush=True)
    client.publish(DATA_TOPIC, MESSAGE_DATA, qos=2)
    MESSAGE_DATA = None


def on_publish(client, userdata, mid):
    global MESSAGE_HASH

    if MESSAGE_HASH is not None:
        print(" done.")
        print("Publishing hash...", end="", flush=True)
        client.publish(HASH_TOPIC, MESSAGE_HASH, qos=2)
        MESSAGE_HASH = None
    else:
        print(" done.")
        print("Subscribing...", end="", flush=True)
        client.subscribe(OK_TOPIC, qos=1)


def on_subscribe(client, userdata, mid, granted_qos):
    print(" done.")
    print("Waiting for OK...", end="", flush=True)


def on_message(client, userdata, message):
    if message.payload == b"1":
        print(" OK.")
        client.disconnect()
    else:
        print(" not OK!")
        client.disconnect()


def main():
    global MESSAGE_DATA, MESSAGE_HASH

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    print(f"Reading {APP_BIN}...", end="", flush=True)
    with open(APP_BIN, "rb") as payload_file:
        MESSAGE_DATA = payload_file.read()
        print(f" done. {len(MESSAGE_DATA)} bytes.")

        print("Hashing...", end="", flush=True)
        MESSAGE_HASH = sha256(MESSAGE_DATA).digest()
        print(" done.")
        print(f"SHA256: {hexlify(MESSAGE_HASH).decode()}")

    print("Connecting to MQTT broker...", end="", flush=True)
    client.connect("pb4_control.local", keepalive=1)
    client.loop_forever()


if __name__ == "__main__":
    main()
