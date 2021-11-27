from binascii import hexlify
from hashlib import sha256

import paho.mqtt.client as mqtt

DEVICE_ID = "dbd5a8"

DATA_TOPIC = f"/pb4/devices/{DEVICE_ID}/ota/app/data"
HASH_TOPIC = f"/pb4/devices/{DEVICE_ID}/ota/app/sha256"
OK_TOPIC = f"/pb4/devices/{DEVICE_ID}/ota/app/ok"

MESSAGE = bytearray()


def on_message(client, userdata, message):
    global MESSAGE

    if message.topic == DATA_TOPIC:
        if len(MESSAGE) == 0:
            print("Receiving", end="", flush=True)
        print(".", end="", flush=True)
        MESSAGE.extend(message.payload)
    elif message.topic == HASH_TOPIC:
        print(" done.")
        app_hash = sha256(MESSAGE).digest()
        if message.payload == app_hash:
            print(f"Received OTA successfully! {len(MESSAGE)} bytes, hash SHA256:{hexlify(app_hash).decode()}")
            print("Sending OK...", end="", flush=True)
            client.publish(OK_TOPIC, "1", qos=1)
        else:
            print(f"Error! Received {len(MESSAGE)} bytes with expected hash SHA256:{hexlify(message.payload).decode()},"
                  f" but actual hash was SHA256:{hexlify(app_hash).decode()}")
            MESSAGE = bytearray()
            print("Sending NOT OK...", end="", flush=True)
            client.publish(OK_TOPIC, "0", qos=1)


def on_publish(client, userdata, mid):
    print(" done.")
    if len(MESSAGE) != 0:
        client.disconnect()


def main():
    client = mqtt.Client()
    client.on_message = on_message
    client.on_publish = on_publish
    client.connect("pb4_control.local", keepalive=1)
    client.subscribe(DATA_TOPIC, 2)
    client.subscribe(HASH_TOPIC, 2)
    print("Waiting...")
    client.loop_forever()


if __name__ == "__main__":
    main()
