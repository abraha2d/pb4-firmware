from os import uname

# noinspection PyUnresolvedReferences
from ds18x20 import DS18X20
# noinspection PyUnresolvedReferences
from esp32 import NVS
# noinspection PyUnresolvedReferences
from machine import I2C, Pin, PWM, Signal, TouchPad
# noinspection PyUnresolvedReferences
from network import AP_IF, STA_IF, WLAN
# noinspection PyUnresolvedReferences
from onewire import OneWire

from uasyncio import sleep_ms


class FakeSignal:
    pass


version = 4 if "PottyBox 4.0" in uname().machine else 2

boot = Signal(0, Pin.IN, invert=True)

exhaust = Signal(13 if version == 4 else 14, Pin.OUT, value=0)
flush_1 = Signal(25 if version == 4 else 12, Pin.OUT, value=0)
flush_2 = Signal(26 if version == 4 else 13, Pin.OUT, value=0)

i2c = I2C(0, sda=Pin(21), scl=Pin(22))

nvs = NVS("pb4")

s1_led = Signal(2, Pin.OUT, value=0) if version == 4 else FakeSignal()
s1_int = Signal(4, Pin.IN, pull=Pin.PULL_UP) if version == 4 else FakeSignal()
s1_shut = Signal(5, Pin.OUT, value=1, invert=True) if version == 4 else FakeSignal()

s2_led = Signal(18, Pin.OUT, value=0) if version == 4 else FakeSignal()
s2_int = Signal(19, Pin.IN, pull=Pin.PULL_UP) if version == 4 else FakeSignal()
s2_shut = Signal(23, Pin.OUT, value=1, invert=True) if version == 4 else FakeSignal()

touch_1_pin = Pin(32)
touch_2_pin = Pin(33)

if version == 2:
    # TODO: Move to WHControl app
    touch_2_pin.init(mode=Pin.OUT, value=1)
    ow = OneWire(touch_1_pin)
    ds = DS18X20(ow)
else:
    touch_1 = TouchPad(touch_1_pin)
    touch_2 = TouchPad(touch_2_pin)

wlan_ap = WLAN(AP_IF)
wlan_sta = WLAN(STA_IF)

if version == 4:
    class StatusLED:
        BLACK = [0, 0, 0]
        BLUE = [0, 0, 1]
        CYAN = [0, 1, 1]
        GREEN = [0, 1, 0]
        MAGENTA = [1, 0, 1]
        RED = [1, 0, 0]
        WHITE = [1, 1, 1]
        YELLOW = [1, 0.5, 0]

        APP_BOOTING = MAGENTA, False
        APP_SHUTDOWN = YELLOW, False

        APP_UPGRADING = YELLOW, True
        APP_RESETTING = MAGENTA, True

        APP_IDLE = GREEN, False
        APP_RUNNING = GREEN, True

        APP_ERROR = RED, False

        NETWORK_SCANNING = BLUE, True
        NETWORK_CONNECTED = BLUE, False
        NETWORK_HOTSPOT = WHITE, False

        def __init__(self):
            self.r = PWM(Pin(27), freq=40000, duty=1023)
            self.g = PWM(Pin(14), freq=40000, duty=1023)
            self.b = PWM(Pin(12), freq=40000, duty=1023)

            self.network_state = None
            self.app_state = None

        def write(self, color):
            r, g, b = color
            self.r.duty(int((1 - r) * 1023))
            self.g.duty(int((1 - g) * 1023))
            self.b.duty(int((1 - b) * 1023))

        async def show(self, color, blink=False):
            if blink:
                for _ in range(10):
                    self.write(color)
                    await sleep_ms(100)
                    self.write(self.BLACK)
                    await sleep_ms(100)
            else:
                self.write(color)
                await sleep_ms(2000)

        async def run(self):
            while True:
                if self.network_state is not None:
                    await self.show(*self.network_state)
                if self.app_state is not None:
                    await self.show(*self.app_state)
                if self.network_state is None and self.app_state is None:
                    await self.show(self.BLACK)
else:
    assert version == 2

    class StatusLED:
        BLACK = 0

        APP_BOOTING = 1, False
        APP_SHUTDOWN = 1, False

        APP_UPGRADING = 1, True
        APP_RESETTING = 1, True

        APP_IDLE = 1, False
        APP_RUNNING = 1, True

        APP_ERROR = 1, False

        NETWORK_SCANNING = 1, True
        NETWORK_CONNECTED = 1, False
        NETWORK_HOTSPOT = 1, False

        def __init__(self):
            self.sl = PWM(Pin(5), freq=40000, duty=1023)

            self.network_state = None
            self.app_state = None

        def write(self, duty):
            self.sl.duty(int(duty * 1023))

        async def show(self, color, blink=False):
            if blink:
                for _ in range(10):
                    self.write(color)
                    await sleep_ms(100)
                    self.write(self.BLACK)
                    await sleep_ms(100)
            else:
                self.write(color)
                await sleep_ms(2000)

        async def run(self):
            while True:
                if self.network_state is not None:
                    await self.show(*self.network_state)
                if self.app_state is not None:
                    await self.show(*self.app_state)
                if self.network_state is None and self.app_state is None:
                    await self.show(self.BLACK)

status = StatusLED()
