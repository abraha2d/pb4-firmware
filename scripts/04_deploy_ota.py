from binascii import hexlify
from hashlib import sha256

import paho.mqtt.client as mqtt

APP_BIN = "build/app.bin"
DEVICE_ID = "dbd5a8"

DATA_TOPIC = f"/pb4/devices/{DEVICE_ID}/ota/app/data"
CHUNK_SIZE = 1433 - len(DATA_TOPIC)
MESSAGE_CHUNKS = None

HASH_TOPIC = f"/pb4/devices/{DEVICE_ID}/ota/app/sha256"
MESSAGE_HASH = None

OK_TOPIC = f"/pb4/devices/{DEVICE_ID}/ota/app/ok"


def on_connect(client, userdata, flags, rc):
    client.on_connect = None
    print(" connected.")
    print("Publishing", end="", flush=True)
    on_publish(client, None, None)


def on_subscribe(client, userdata, mid, granted_qos):
    print(" subscribed.")
    print("Waiting for OK...", end="", flush=True)


def on_publish(client, userdata, mid):
    global MESSAGE_CHUNKS, MESSAGE_HASH

    if len(MESSAGE_CHUNKS) > 0:
        print(".", end="", flush=True)
        client.publish(DATA_TOPIC, MESSAGE_CHUNKS[0], qos=2)
        MESSAGE_CHUNKS = MESSAGE_CHUNKS[1:]
    elif MESSAGE_HASH is not None:
        print(" published.")
        print("Publishing hash...", end="", flush=True)
        client.publish(HASH_TOPIC, MESSAGE_HASH, qos=2)
        MESSAGE_HASH = None
    else:
        print(" published.")
        print("Subscribing...", end="", flush=True)
        client.subscribe(OK_TOPIC, 1)


def on_message(client, userdata, message):
    if message.payload == b"1":
        print(" done.")
        client.disconnect()
    else:
        print(" not OK...")
        client.disconnect()


def main():
    global MESSAGE_CHUNKS, MESSAGE_HASH

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish
    client.on_message = on_message

    print(f"Reading {APP_BIN}...", end="", flush=True)
    with open(APP_BIN, "rb") as payload_file:
        payload = payload_file.read()
        print(" done.")
        print(f"Read {len(payload)} bytes from {APP_BIN}.")

        print("Hashing...", end="", flush=True)
        MESSAGE_HASH = sha256(payload).digest()
        print(" done.")
        print(f"SHA256: {hexlify(MESSAGE_HASH).decode()}")

        print("Chunking...", end="", flush=True)
        MESSAGE_CHUNKS = [payload[i:i + CHUNK_SIZE] for i in range(0, len(payload), CHUNK_SIZE)]
        print(" done.")
        print(f"{len(MESSAGE_CHUNKS)} chunks, max chunk size of {CHUNK_SIZE} bytes.")

    print("Connecting to MQTT broker...", end="", flush=True)
    client.connect("pb4_control.local", keepalive=1)
    client.loop_forever()


if __name__ == "__main__":
    main()
