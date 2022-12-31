from binascii import hexlify
from time import time

# noinspection PyUnresolvedReferences
import ds18x20

# noinspection PyUnresolvedReferences
import onewire
from uasyncio import sleep_ms, sleep

from mqtt.property import MqttBoolProp, MqttFloatProp, MqttIntProp, MqttProp
from upy_platform import exhaust, status, touch_1_pin
from .config import (
    MQTT_TOPIC_ALERT_MISSING_SENSOR,
    MQTT_TOPIC_ALERT_CONDENSATION_CUTOFF,
    MQTT_TOPIC_ALERT_SAFETY_CUTOFF,
    MQTT_TOPIC_ALERT_MAX_RUNTIME,
    MQTT_TOPIC_ALERT_IGNITER_CHECK,
    MQTT_TOPIC_HEAT_CUTOFF_CONDENSATION,
    MQTT_TOPIC_HEAT_CUTOFF_SAFETY,
    MQTT_TOPIC_HEAT_MAX_RUNTIME,
    MQTT_TOPIC_HEAT_OVERRIDE,
    MQTT_TOPIC_HEAT_SETPOINT,
    MQTT_TOPIC_IGNITER_CHECK_DELAY,
    MQTT_TOPIC_IGNITER_CHECK_THRESHOLD,
    MQTT_TOPIC_IGNITER_COOLOFF_DELAY,
    MQTT_TOPIC_OUTPUT_HEAT_ON,
    MQTT_TOPIC_OUTPUT_TEMP_BOTTOM,
    MQTT_TOPIC_OUTPUT_TEMP_TOP,
    MQTT_TOPIC_SENSOR_ID_TOP,
    MQTT_TOPIC_SENSOR_ID_BOTTOM,
)


class OneWire(onewire.OneWire):
    def pullup(self, strong=False):
        if strong:
            self.pin.init(self.pin.OUT, value=1)
        else:
            self.pin.init(self.pin.OPEN_DRAIN, self.pin.PULL_UP, value=1)

    def reset(self, required=False):
        self.pullup()  # needed to restore Open Drain Output
        return super().reset(required)


class DS18X20(ds18x20.DS18X20):
    def convert_temp(self):
        self.ow.reset(True)
        self.ow.writebyte(self.ow.SKIP_ROM)
        self.ow.pullup(strong=True)  # strong pullup *before* convert
        self.ow.writebyte(0x44)


async def main(mqtt_client):
    ds = DS18X20(OneWire(touch_1_pin))

    # Static configuration
    sensor_id_top = MqttProp(mqtt_client, MQTT_TOPIC_SENSOR_ID_TOP, readonly=True)
    sensor_id_bottom = MqttProp(mqtt_client, MQTT_TOPIC_SENSOR_ID_BOTTOM, readonly=True)

    # Dynamic configuration
    heat_cutoff_condensation = MqttIntProp(
        mqtt_client, MQTT_TOPIC_HEAT_CUTOFF_CONDENSATION, 100, readonly=True
    )
    heat_cutoff_safety = MqttIntProp(
        mqtt_client, MQTT_TOPIC_HEAT_CUTOFF_SAFETY, 140, readonly=True
    )
    heat_max_runtime = MqttIntProp(
        mqtt_client, MQTT_TOPIC_HEAT_MAX_RUNTIME, 900, readonly=True
    )
    heat_override = MqttBoolProp(
        mqtt_client, MQTT_TOPIC_HEAT_OVERRIDE, False, readonly=True
    )
    heat_setpoint = MqttIntProp(
        mqtt_client, MQTT_TOPIC_HEAT_SETPOINT, 120, readonly=True
    )

    igniter_check_delay = MqttIntProp(
        mqtt_client, MQTT_TOPIC_IGNITER_CHECK_DELAY, 120, readonly=True
    )
    igniter_check_threshold = MqttIntProp(
        mqtt_client, MQTT_TOPIC_IGNITER_CHECK_THRESHOLD, 110, readonly=True
    )
    igniter_cooloff_delay = MqttIntProp(
        mqtt_client, MQTT_TOPIC_IGNITER_COOLOFF_DELAY, 10, readonly=True
    )

    # Local state
    heat_start = None
    igniter_good = False

    # Alerts
    missing_sensor_alert = MqttBoolProp(
        mqtt_client, MQTT_TOPIC_ALERT_MISSING_SENSOR, writeonly=True
    )
    condensation_cutoff_alert = MqttBoolProp(
        mqtt_client, MQTT_TOPIC_ALERT_CONDENSATION_CUTOFF, writeonly=True
    )
    safety_cutoff_alert = MqttBoolProp(
        mqtt_client, MQTT_TOPIC_ALERT_SAFETY_CUTOFF, writeonly=True
    )
    max_runtime_alert = MqttBoolProp(
        mqtt_client, MQTT_TOPIC_ALERT_MAX_RUNTIME, writeonly=True
    )
    igniter_check_alert = MqttBoolProp(
        mqtt_client, MQTT_TOPIC_ALERT_IGNITER_CHECK, writeonly=True
    )

    # Output
    heat_on = MqttBoolProp(mqtt_client, MQTT_TOPIC_OUTPUT_HEAT_ON, writeonly=True)
    temp_top = MqttFloatProp(mqtt_client, MQTT_TOPIC_OUTPUT_TEMP_TOP, writeonly=True)
    temp_bottom = MqttFloatProp(
        mqtt_client, MQTT_TOPIC_OUTPUT_TEMP_BOTTOM, writeonly=True
    )

    def start_heat():
        nonlocal heat_start
        heat_start = time()
        exhaust.on()
        heat_on.set(True)

    def stop_heat():
        nonlocal heat_start
        heat_on.set(False)
        exhaust.off()
        heat_start = None

    while True:
        # Check max runtime
        if heat_start is not None and time() - heat_start > heat_max_runtime.get():
            print(f"apps.whcontrol.main: Error: max runtime exceeded, shutting down...")
            stop_heat()
            status.app_state = status.APP_ERROR
            max_runtime_alert.set(True)
            while True:
                await sleep(1)
        max_runtime_alert.set(False)

        await sleep_ms(250)
        try:
            ds.convert_temp()
        except onewire.OneWireError:
            continue
        await sleep_ms(750)

        temps = {}
        for rom in sorted(ds.scan()):
            try:
                temps[hexlify(rom)] = ds.read_temp(rom) * 9 / 5 + 32
            except Exception:  # TODO: cast a smaller net
                pass

        try:
            print()
            temp_top.set(temps[sensor_id_top.get()])
            print(f"Top:    {temp_top.get()}")
            temp_bottom.set(temps[sensor_id_bottom.get()])
            print(f"Bottom: {temp_bottom.get()}")
        except KeyError as e:
            # print(f"apps.whcontrol.main: Missing configured temperature sensor: {e}")
            missing_sensor_alert.set(True)
            continue
        missing_sensor_alert.set(False)

        # Check safety cutoff
        if temp_top.get() > heat_cutoff_safety.get():
            if heat_start is not None:
                print(f"apps.whcontrol.main: Warning: safety cutoff triggered.")
                stop_heat()
            safety_cutoff_alert.set(True)
            continue
        safety_cutoff_alert.set(False)

        # Check if igniter is working
        if (
            heat_start is not None
            and not igniter_good
            and time() - heat_start > igniter_check_delay.get()
        ):
            if temp_top.get() > igniter_check_threshold.get():
                igniter_good = True
            else:
                print(
                    f"apps.whcontrol.main: Warning: igniter failure detected,"
                    + " cooling off..."
                )
                stop_heat()
                igniter_check_alert.set(True)
                await sleep(igniter_cooloff_delay.get())
                continue
        igniter_check_alert.set(False)

        # Check condensation cutoff
        if temp_bottom.get() > heat_cutoff_condensation.get():
            if heat_start is not None:
                print(f"apps.whcontrol.main: Condensation cutoff triggered.")
                stop_heat()
            condensation_cutoff_alert.set(True)
            continue
        condensation_cutoff_alert.set(False)

        if heat_override.get():
            if heat_start is None:
                print(f"apps.whcontrol.main: Starting heat due to manual request...")
                start_heat()
            continue

        if temp_bottom.get() > heat_setpoint.get():
            if heat_start is not None:
                print(f"apps.whcontrol.main: Stopping heat due to setpoint...")
                stop_heat()
            continue

        if temp_top.get() < heat_setpoint.get():
            if heat_start is None:
                print(f"apps.whcontrol.main: Starting heat due to setpoint...")
                start_heat()
            continue
