from errno import ENODEV

from time import ticks_ms, ticks_diff
from uasyncio import sleep_ms, create_task

from drivers import BUS_S1, BUS_S2, BUS_QWIIC
from drivers.vl53l1x import get_sensor_on_bus
from mqtt.property import MqttFloatProp
from upy_platform import s1_led, s2_led, exhaust

from .config import (
    MQTT_TOPIC_EXHAUST_TIME,
    get_on_threshold_topic,
    get_off_threshold_topic,
    MQTT_TOPIC_EXHAUST_DELAY,
)
from ..pb_flush.config import LOOP_TIME


async def main(mqtt_client):
    # dual_potty = MqttBoolProp(mqtt_client, MQTT_TOPIC_DUAL_POTTY, False, readonly=True)
    exhaust_delay = MqttFloatProp(
        mqtt_client, MQTT_TOPIC_EXHAUST_DELAY, 0, readonly=True
    )
    exhaust_time = MqttFloatProp(
        mqtt_client, MQTT_TOPIC_EXHAUST_TIME, 30, readonly=True
    )

    sensor_bus = [BUS_S1, BUS_S2]
    blinkenlite = [s1_led, s2_led]
    ex_request = [False, False]

    def process_sensor(idx):
        on_threshold = MqttFloatProp(
            mqtt_client, get_on_threshold_topic(sensor_bus[idx]), 300, readonly=True
        )
        off_threshold = MqttFloatProp(
            mqtt_client, get_off_threshold_topic(sensor_bus[idx]), 600, readonly=True
        )

        while True:
            try:
                print(f"pb_exhaust.main: Waiting for {sensor_bus[idx]}...")
                s = None
                while s is None:
                    await sleep_ms(100)
                    s = get_sensor_on_bus(sensor_bus[idx], return_first=True)

                print(f"pb_exhaust.main: Starting {sensor_bus[idx]}...")
                # s.set_distance_mode(1)
                # s.set_inter_measurement_ms(15)
                # s.set_timing_budget_ms(15)
                s.start_ranging()

                distance = await s.get_distance()
                blinkenlite[idx].off()
                event_time = ticks_ms()

                while True:
                    d = await s.get_distance()

                    # Implement hysteresis
                    if d < on_threshold.get() < distance:
                        blinkenlite[idx].on()
                        event_time = ticks_ms()
                    elif d > off_threshold.get() > distance:
                        blinkenlite[idx].off()
                        event_time = ticks_ms()

                    if (
                        ex_request[idx] is False
                        and blinkenlite[idx].value() == 1
                        and ticks_diff(ticks_ms(), event_time)
                        > exhaust_delay.get() * 1000
                    ):
                        ex_request[idx] = True
                    elif (
                        ex_request[idx] is True
                        and blinkenlite[idx].value() == 0
                        and ticks_diff(ticks_ms(), event_time)
                        > exhaust_time.get() * 1000
                    ):
                        ex_request[idx] = False

                    distance = d

            except OSError as e:
                ex_request[idx] = False
                if e.errno == ENODEV:
                    print(f"pb_exhaust.main: {sensor_bus[idx]} disconnected.")
                    continue
                raise

    for i in range(len(sensor_bus)):
        create_task(process_sensor(i))

    while True:
        exhaust.value(any(ex_request))
        await sleep_ms(LOOP_TIME)
