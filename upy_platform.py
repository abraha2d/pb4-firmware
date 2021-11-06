from _thread import allocate_lock, start_new_thread
from time import sleep_ms

from esp32 import NVS
from machine import I2C, Pin, PWM, Signal, TouchPad
from network import AP_IF, STA_IF, WLAN

exhaust = Signal(13, Pin.OUT, value=0)
flush_1 = Signal(25, Pin.OUT, value=0)
flush_2 = Signal(26, Pin.OUT, value=0)

i2c = I2C(0, sda=Pin(21), scl=Pin(22))

nvs = NVS("pb4")

s1_led = Signal(2, Pin.OUT, value=0)
s1_int = Signal(4, Pin.IN, pull=Pin.PULL_UP)
s1_shut = Signal(5, Pin.OUT, value=1, invert=True)

s2_led = Signal(18, Pin.OUT, value=0)
s2_int = Signal(19, Pin.IN, pull=Pin.PULL_UP)
s2_shut = Signal(23, Pin.OUT, value=1, invert=True)

touch_1 = TouchPad(Pin(32))
touch_2 = TouchPad(Pin(33))

wlan_ap = WLAN(AP_IF)
wlan_sta = WLAN(STA_IF)


class StatusLED:
    BLACK = [0, 0, 0]
    BLUE = [0, 0, 1]
    CYAN = [0, 1, 1]
    GREEN = [0, 1, 0]
    MAGENTA = [1, 0, 1]
    RED = [1, 0, 0]
    WHITE = [1, 1, 1]
    YELLOW = [1, 1, 0]

    APP_TIMESYNC = MAGENTA, False
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

        self.run_lock = allocate_lock()
        self.should_run = False

    def write(self, color):
        r, g, b = color
        self.r.duty(int((1 - r) * 512 + 511))
        self.g.duty(int((1 - g) * 512 + 511))
        self.b.duty(int((1 - b) * 512 + 511))

    def show(self, color, blink=False):
        if blink:
            for _ in range(10):
                self.write(color)
                sleep_ms(100)
                self.write(self.BLACK)
                sleep_ms(100)
        else:
            self.write(color)
            sleep_ms(2000)

    def start(self):
        self.should_run = True
        start_new_thread(self.run, ())

    def run(self):
        with self.run_lock:
            while self.should_run:
                if self.network_state is not None:
                    self.show(*self.network_state)
                if self.app_state is not None:
                    self.show(*self.app_state)
                if self.network_state is None and self.app_state is None:
                    self.write(self.BLACK)

    def stop(self):
        self.should_run = False
        while self.run_lock.locked():
            pass


status = StatusLED()
status.start()
