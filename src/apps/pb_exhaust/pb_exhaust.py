from uasyncio import sleep_ms

from drivers import BUS_S1
from drivers.vl53l1x import get_sensor_on_bus
from mqtt.property import MqttFloatProp

from .config import MQTT_TOPIC_EXHAUST_TIME


async def main(mqtt_client):
    # dual_potty = MqttBoolProp(mqtt_client, MQTT_TOPIC_DUAL_POTTY, False, readonly=True)
    exhaust_time = MqttFloatProp(
        mqtt_client, MQTT_TOPIC_EXHAUST_TIME, 30, readonly=True
    )

    while True:
        try:
            print(f"pb_exhaust.main: Waiting for sensor 1...")
            s1 = None
            while s1 is None:
                await sleep_ms(100)
                s1 = get_sensor_on_bus(BUS_S1)

            print(f"pb_exhaust.main: Starting sensor 1...")
            # s1.set_distance_mode(1)
            # s1.set_inter_measurement_ms(15)
            # s1.set_timing_budget_ms(15)
            s1.start_ranging()

            while True:
                d = await s1.get_distance()
                print(f"pb_exhaust.main: Sensor 1 distance: {d}mm")
        except OSError:
            print(f"pb_exhaust.main: Sensor 1 disconnected.")
