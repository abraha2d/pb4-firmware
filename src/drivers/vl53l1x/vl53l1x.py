from uasyncio import sleep_ms

from drivers import register_address, readfrom_mem, writeto_mem, BUS_QWIIC

from .constants import *


SENSOR_BUS_MAP = {BUS_QWIIC: []}


def get_sensor_on_bus(device_bus):
    return SENSOR_BUS_MAP.get(device_bus, None)


def remove_sensor_from_map(sensor):
    for b in SENSOR_BUS_MAP.keys():
        if type(SENSOR_BUS_MAP[b]) == list and sensor in SENSOR_BUS_MAP[b]:
            SENSOR_BUS_MAP[b].pop(sensor)
        elif SENSOR_BUS_MAP[b] == sensor:
            SENSOR_BUS_MAP.pop(b)


class VL53L1X:
    def __init__(self, i2c_addr):
        self.i2c_addr = i2c_addr

    def readfrom_mem(self, memaddr, nbytes):
        try:
            return readfrom_mem(self.i2c_addr, memaddr, nbytes, addrsize=16)
        except OSError:
            remove_sensor_from_map(self)
            raise

    def writeto_mem(self, memaddr, buf):
        try:
            return writeto_mem(self.i2c_addr, memaddr, buf, addrsize=16)
        except OSError:
            remove_sensor_from_map(self)
            raise

    async def init_sensor(self):
        # Wait for device booted
        while True:
            await sleep_ms(2)
            d = self.readfrom_mem(VL53L1_FIRMWARE__SYSTEM_STATUS, 1)
            if d[0] & 0x01:
                break

        # Sensor init
        self.writeto_mem(0x2D, bytes(DEFAULT_CONFIGURATION))

        self.start_ranging()
        await self.get_distance(read=False)
        self.stop_ranging()

        self.writeto_mem(
            VL53L1_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND, b"\x09"
        )  # two bounds VHV
        self.writeto_mem(0x0B, b"\x00")  # start VHV from the previous temperature

    def set_i2c_address(self, i2c_addr):
        self.writeto_mem(VL53L1_I2C_SLAVE__DEVICE_ADDRESS, i2c_addr.to_bytes(1, "big"))
        self.i2c_addr = i2c_addr

    def start_ranging(self):
        self.writeto_mem(SYSTEM__MODE_START, b"\x40")

    def stop_ranging(self):
        self.writeto_mem(SYSTEM__MODE_START, b"\x00")

    async def get_distance(self, read=True):
        # Get interrupt polarity
        d = self.readfrom_mem(GPIO_HV_MUX__CTRL, 1)
        p = ((d[0] & 0x10) >> 4) ^ 1

        # Check for data ready
        while True:
            await sleep_ms(1)
            d = self.readfrom_mem(GPIO__TIO_HV_STATUS, 1)
            if d[0] & 1 == p:
                break

        if read:
            # Get distance
            d = self.readfrom_mem(
                VL53L1_RESULT__FINAL_CROSSTALK_CORRECTED_RANGE_MM_SD0, 2
            )
        else:
            d = None

        # Clear interrupt
        self.writeto_mem(SYSTEM__INTERRUPT_CLEAR, b"\x01")

        return d and int.from_bytes(d, "big")

    def get_distance_mode(self):
        d = self.readfrom_mem(PHASECAL_CONFIG__TIMEOUT_MACROP, 1)
        if d[0] == 0x14:
            return 1
        elif d[0] == 0x0A:
            return 2
        else:
            print(f"drivers.vl53l1x.get_distance_mode: Invalid distance mode: {d}")
            return 0

    def set_distance_mode(self, distance_mode):
        # distance_mode: Short (1) or Long (2)
        timing_budget = self.get_timing_budget_ms()
        if distance_mode == 1:
            self.writeto_mem(PHASECAL_CONFIG__TIMEOUT_MACROP, b"\x14")
            self.writeto_mem(RANGE_CONFIG__VCSEL_PERIOD_A, b"\x07")
            self.writeto_mem(RANGE_CONFIG__VCSEL_PERIOD_B, b"\x05")
            self.writeto_mem(RANGE_CONFIG__VALID_PHASE_HIGH, b"\x38")
            self.writeto_mem(SD_CONFIG__WOI_SD0, b"\x07\x05")
            self.writeto_mem(SD_CONFIG__INITIAL_PHASE_SD0, b"\x06\x06")
        elif distance_mode == 2:
            self.writeto_mem(PHASECAL_CONFIG__TIMEOUT_MACROP, b"\x0A")
            self.writeto_mem(RANGE_CONFIG__VCSEL_PERIOD_A, b"\x0F")
            self.writeto_mem(RANGE_CONFIG__VCSEL_PERIOD_B, b"\x0D")
            self.writeto_mem(RANGE_CONFIG__VALID_PHASE_HIGH, b"\xB8")
            self.writeto_mem(SD_CONFIG__WOI_SD0, b"\x0F\x0D")
            self.writeto_mem(SD_CONFIG__INITIAL_PHASE_SD0, b"\x0E\x0E")
        else:
            print(
                f"drivers.vl53l1x.set_distance_mode: Invalid distance mode: {distance_mode}"
            )
        self.set_timing_budget_ms(timing_budget)

    def set_inter_measurement_ms(self, imp):
        d = self.readfrom_mem(VL53L1_RESULT__OSC_CALIBRATE_VAL, 2)
        clock_pll = int.from_bytes(d, "big") & 0x3FF
        to_write = int(clock_pll * imp * 1.075).to_bytes(4, "big")
        self.writeto_mem(VL53L1_SYSTEM__INTERMEASUREMENT_PERIOD, to_write)

    def get_timing_budget_ms(self):
        d = self.readfrom_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, 2)
        if d == 0x001D:
            return 15
        elif d == 0x0051 or d == 0x001E:
            return 20
        elif d == 0x00D6 or d == 0x0060:
            return 33
        elif d == 0x1AE or d == 0x00AD:
            return 50
        elif d == 0x2E1 or d == 0x01CC:
            return 100
        elif d == 0x03E1 or d == 0x02D9:
            return 200
        elif d == 0x0591 or d == 0x048F:
            return 500
        else:
            print(f"drivers.vl53l1x.get_timing_budget_ms: Invalid timing budget: {d}")
            return 0

    def set_timing_budget_ms(self, timing_budget):
        distance_mode = self.get_distance_mode()
        if distance_mode == 0:
            print(
                f"drivers.vl53l1x.set_timing_budget_ms: Invalid distance mode: {distance_mode}"
            )
        elif distance_mode == 1:
            if timing_budget == 15:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\x1D")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x27")
            elif timing_budget == 20:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\x51")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x6E")
            elif timing_budget == 33:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\xD6")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x6E")
            elif timing_budget == 50:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x01\xAE")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x01\xE8")
            elif timing_budget == 100:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x02\xE1")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x03\x88")
            elif timing_budget == 200:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x03\xE1")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x04\x96")
            elif timing_budget == 500:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x05\x91")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x05\xC1")
            else:
                print(
                    f"drivers.vl53l1x.set_timing_budget_ms: Invalid timing budget: {timing_budget}"
                )
        else:
            if timing_budget == 20:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\x1E")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x22")
            elif timing_budget == 33:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\x60")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x6E")
            elif timing_budget == 50:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\xAD")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\xC6")
            elif timing_budget == 100:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x01\xCC")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x01\xEA")
            elif timing_budget == 200:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x02\xD9")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x02\xF8")
            elif timing_budget == 500:
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x04\x8F")
                self.writeto_mem(RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x04\xA4")
            else:
                print(
                    f"drivers.vl53l1x.set_timing_budget_ms: Invalid timing budget: {timing_budget}"
                )


async def handle_new_sensor(device_bus, device_addr, open_addrs):
    v = VL53L1X(device_addr)
    await v.init_sensor()

    try:
        v.set_i2c_address(next(iter(open_addrs)))
    except StopIteration:
        print("drivers.vl53l1x.handle_newsensor: No more open addresses!")

    if device_bus == BUS_QWIIC:
        SENSOR_BUS_MAP[device_bus].append(v)
    else:
        SENSOR_BUS_MAP[device_bus] = v

    return v.i2c_addr


def register():
    register_address(0x29, "vl53l1x", handle_new_sensor)
