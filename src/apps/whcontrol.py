from binascii import hexlify

from time import time

# noinspection PyUnresolvedReferences
import ds18x20
# noinspection PyUnresolvedReferences
import onewire
from machine import Pin
from uasyncio import sleep_ms, sleep

from upy_platform import exhaust, status, touch_1_pin

NAME = "WHControl"


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
    # TODO: get config from MQTT
    sensor_id_top = "28ff8821a2170546"
    sensor_id_bottom = "28ffab16a217053e"

    # Dynamic configuration
    # TODO: get config from MQTT
    heat_cutoff_condensation = 100
    heat_cutoff_safety = 140
    heat_max_runtime = 900
    heat_override = False
    heat_setpoint = 120

    igniter_check_time = 120
    igniter_cooloff_time = 10
    igniter_threshold = 110

    # Local state
    heat_start = None
    igniter_good = False

    def start_heat():
        nonlocal heat_start
        heat_start = time()
        exhaust.on()

    def stop_heat():
        nonlocal heat_start
        exhaust.off()
        heat_start = None

    while True:
        # Check max runtime
        if heat_start is not None and time() - heat_start > heat_max_runtime:
            print(f"apps.whcontrol.main: Error: max runtime exceeded, shutting down...")
            stop_heat()
            status.app_state = status.APP_ERROR
            while True:
                await sleep(1)

        await sleep_ms(250)
        ds.convert_temp()
        await sleep_ms(750)

        temps = {}
        for rom in sorted(ds.scan()):
            try:
                temps[hexlify(rom).decode()] = ds.read_temp(rom) * 9 / 5 + 32
            except Exception:
                pass

        try:
            print()
            temp_top = temps[sensor_id_top]
            print(f"Top:    {temp_top}")
            temp_bottom = temps[sensor_id_bottom]
            print(f"Bottom: {temp_bottom}")
        except KeyError as e:
            print(f"apps.whcontrol.main: Missing configured temperature sensor: {e}")
            continue

        # Check safety cutoff
        if temp_top > heat_cutoff_safety:
            if heat_start is not None:
                print(f"apps.whcontrol.main: Warning: safety cutoff triggered.")
                stop_heat()
            continue

        # Check if igniter is working
        if heat_start is not None and not igniter_good and time() - heat_start > igniter_check_time:
            if temp_top > igniter_threshold:
                igniter_good = True
            else:
                print(f"apps.whcontrol.main: Warning: igniter failure detected, cooling off...")
                stop_heat()
                await sleep(igniter_cooloff_time)
                continue

        # Check condensation cutoff
        if temp_bottom > heat_cutoff_condensation:
            if heat_start is not None:
                print(f"apps.whcontrol.main: Condensation cutoff triggered.")
                stop_heat()
            continue

        if heat_override:
            if heat_start is None:
                print(f"apps.whcontrol.main: Starting heat due to manual request...")
                start_heat()
            continue

        if temp_bottom > heat_setpoint:
            if heat_start is not None:
                print(f"apps.whcontrol.main: Stopping heat due to setpoint...")
                stop_heat()
            continue

        if temp_top < heat_setpoint:
            if heat_start is None:
                print(f"apps.whcontrol.main: Starting heat due to setpoint...")
                start_heat()
            continue
