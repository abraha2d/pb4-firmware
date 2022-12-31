from time import ticks_ms, ticks_diff

from uasyncio import sleep_ms

from mqtt.property import MqttBoolProp, MqttFloatProp
from upy_platform import flush_1, flush_2, touch_1, touch_2
from .config import (
    CAL_ALPHA,
    LOOP_TIME,
    MQTT_TOPIC_DUAL_POTTY,
    MQTT_TOPIC_FLUSH_TIME,
    THRESHOLD,
)


async def main(mqtt_client):
    dual_potty = MqttBoolProp(mqtt_client, MQTT_TOPIC_DUAL_POTTY, False, readonly=True)
    flush_time = MqttFloatProp(mqtt_client, MQTT_TOPIC_FLUSH_TIME, 3, readonly=True)

    touch_pad = [touch_1, touch_2]
    touch_avg = [None, None]
    flush_start = [None, None]
    flush_sig = [flush_1, flush_2]

    def process_touch(idx):
        try:
            touch_val = touch_pad[idx].read()
        except ValueError:
            return

        if touch_avg[idx] is None:
            touch_avg[idx] = touch_val

        pressed = touch_val < touch_avg[idx] * THRESHOLD

        if not pressed:
            touch_avg[idx] = (1 - CAL_ALPHA) * touch_avg[idx] + CAL_ALPHA * touch_val
        elif flush_start[idx] is None:
            flush_start[idx] = ticks_ms()

        flush_val = pressed or (
            flush_start[idx] is not None
            and ticks_diff(ticks_ms(), flush_start[idx]) < flush_time.get() * 1000
        )

        if not flush_val:
            flush_start[idx] = None

        flush_sig[idx].value(flush_val)

    while True:
        process_touch(0)
        if dual_potty.get():
            process_touch(1)
        await sleep_ms(LOOP_TIME)
