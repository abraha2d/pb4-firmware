from uasyncio import sleep_ms

from mqtt.property import MqttFloatProp
from upy_platform import (
    i2c,
    s1_en,
    s2_en,
)
from .config import (
    I2C_ADDR,
    MQTT_TOPIC_EXHAUST_TIME,
)
from .vl53l1_config import DEFAULT_CONFIG
from .vl53l1_register_map import (
    VL53L1_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND,
    GPIO_HV_MUX__CTRL,
    GPIO__TIO_HV_STATUS,
    PHASECAL_CONFIG__TIMEOUT_MACROP,
    RANGE_CONFIG__TIMEOUT_MACROP_A_HI,
    RANGE_CONFIG__VCSEL_PERIOD_A,
    RANGE_CONFIG__TIMEOUT_MACROP_B_HI,
    RANGE_CONFIG__VCSEL_PERIOD_B,
    RANGE_CONFIG__VALID_PHASE_HIGH,
    VL53L1_SYSTEM__INTERMEASUREMENT_PERIOD,
    SD_CONFIG__WOI_SD0,
    SD_CONFIG__INITIAL_PHASE_SD0,
    SYSTEM__INTERRUPT_CLEAR,
    SYSTEM__MODE_START,
    VL53L1_RESULT__FINAL_CROSSTALK_CORRECTED_RANGE_MM_SD0,
    VL53L1_RESULT__OSC_CALIBRATE_VAL,
    VL53L1_FIRMWARE__SYSTEM_STATUS,
)


async def readfrom_mem(addr, memaddr, nbytes, *, addrsize=16):
    return i2c.readfrom_mem(addr, memaddr, nbytes, addrsize=addrsize)


async def writeto_mem(addr, memaddr, buf, *, addrsize=16):
    return i2c.writeto_mem(addr, memaddr, buf, addrsize=addrsize)


async def get_distance_mode(i2c_addr=I2C_ADDR):
    d = await readfrom_mem(i2c_addr, PHASECAL_CONFIG__TIMEOUT_MACROP, 1)
    if d[0] == 0x14:
        return 1
    elif d[0] == 0x0A:
        return 2
    else:
        print(f"apps.pb_exhaust.get_distance_mode: Invalid distance mode: {d}")
        return 0


async def set_distance_mode(distance_mode, i2c_addr=I2C_ADDR):
    # distance_mode: Short (1) or Long (2)
    timing_budget = await get_timing_budget_ms(i2c_addr)
    if distance_mode == 1:
        await writeto_mem(i2c_addr, PHASECAL_CONFIG__TIMEOUT_MACROP, b"\x14")
        await writeto_mem(i2c_addr, RANGE_CONFIG__VCSEL_PERIOD_A, b"\x07")
        await writeto_mem(i2c_addr, RANGE_CONFIG__VCSEL_PERIOD_B, b"\x05")
        await writeto_mem(i2c_addr, RANGE_CONFIG__VALID_PHASE_HIGH, b"\x38")
        await writeto_mem(i2c_addr, SD_CONFIG__WOI_SD0, b"\x07\x05")
        await writeto_mem(i2c_addr, SD_CONFIG__INITIAL_PHASE_SD0, b"\x06\x06")
    elif distance_mode == 2:
        await writeto_mem(i2c_addr, PHASECAL_CONFIG__TIMEOUT_MACROP, b"\x0A")
        await writeto_mem(i2c_addr, RANGE_CONFIG__VCSEL_PERIOD_A, b"\x0F")
        await writeto_mem(i2c_addr, RANGE_CONFIG__VCSEL_PERIOD_B, b"\x0D")
        await writeto_mem(i2c_addr, RANGE_CONFIG__VALID_PHASE_HIGH, b"\xB8")
        await writeto_mem(i2c_addr, SD_CONFIG__WOI_SD0, b"\x0F\x0D")
        await writeto_mem(i2c_addr, SD_CONFIG__INITIAL_PHASE_SD0, b"\x0E\x0E")
    else:
        print(
            f"apps.pb_exhaust.set_distance_mode: Invalid distance mode: {distance_mode}"
        )
    await set_timing_budget_ms(timing_budget)


async def set_inter_measurement_ms(imp, i2c_addr=I2C_ADDR):
    d = await readfrom_mem(i2c_addr, VL53L1_RESULT__OSC_CALIBRATE_VAL, 2)
    clock_pll = int.from_bytes(d, "big") & 0x3FF
    to_write = int(clock_pll * imp * 1.075).to_bytes(4, "big")
    await writeto_mem(i2c_addr, VL53L1_SYSTEM__INTERMEASUREMENT_PERIOD, to_write)


async def get_timing_budget_ms(i2c_addr=I2C_ADDR):
    d = await readfrom_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, 2)
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
        print(f"apps.pb_exhaust.get_timing_budget_ms: Invalid timing budget: {d}")
        return 0


async def set_timing_budget_ms(timing_budget, i2c_addr=I2C_ADDR):
    distance_mode = await get_distance_mode(i2c_addr)
    if distance_mode == 0:
        print(
            f"apps.pb_exhaust.set_timing_budget_ms: Invalid distance mode: {distance_mode}"
        )
    elif distance_mode == 1:
        if timing_budget == 15:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\x1D")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x27")
        elif timing_budget == 20:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\x51")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x6E")
        elif timing_budget == 33:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\xD6")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x6E")
        elif timing_budget == 50:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x01\xAE")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x01\xE8")
        elif timing_budget == 100:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x02\xE1")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x03\x88")
        elif timing_budget == 200:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x03\xE1")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x04\x96")
        elif timing_budget == 500:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x05\x91")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x05\xC1")
        else:
            print(
                f"apps.pb_exhaust.set_timing_budget_ms: Invalid timing budget: {timing_budget}"
            )
    else:
        if timing_budget == 20:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\x1E")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x22")
        elif timing_budget == 33:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\x60")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\x6E")
        elif timing_budget == 50:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x00\xAD")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x00\xC6")
        elif timing_budget == 100:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x01\xCC")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x01\xEA")
        elif timing_budget == 200:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x02\xD9")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x02\xF8")
        elif timing_budget == 500:
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_A_HI, b"\x04\x8F")
            await writeto_mem(i2c_addr, RANGE_CONFIG__TIMEOUT_MACROP_B_HI, b"\x04\xA4")
        else:
            print(
                f"apps.pb_exhaust.set_timing_budget_ms: Invalid timing budget: {timing_budget}"
            )


async def start_ranging(i2c_addr=I2C_ADDR):
    await writeto_mem(i2c_addr, SYSTEM__MODE_START, b"\x40")


async def get_distance(i2c_addr=I2C_ADDR, read=True):
    # Get interrupt polarity
    d = await readfrom_mem(i2c_addr, GPIO_HV_MUX__CTRL, 1)
    p = ((d[0] & 0x10) >> 4) ^ 1

    # Check for data ready
    while True:
        await sleep_ms(1)
        d = await readfrom_mem(i2c_addr, GPIO__TIO_HV_STATUS, 1)
        if d[0] & 1 == p:
            break

    if read:
        # Get distance
        d = await readfrom_mem(
            i2c_addr, VL53L1_RESULT__FINAL_CROSSTALK_CORRECTED_RANGE_MM_SD0, 2
        )
    else:
        d = None

    # Clear interrupt
    await writeto_mem(i2c_addr, SYSTEM__INTERRUPT_CLEAR, b"\x01")

    return d


async def stop_ranging(i2c_addr=I2C_ADDR):
    await writeto_mem(i2c_addr, SYSTEM__MODE_START, b"\x00")


async def init_sensor():
    # Wait for device booted
    while True:
        await sleep_ms(2)
        d = await readfrom_mem(I2C_ADDR, VL53L1_FIRMWARE__SYSTEM_STATUS, 1)
        if d[0] & 0x01:
            break

    # Sensor init
    await writeto_mem(I2C_ADDR, 0x2D, bytes(DEFAULT_CONFIG))

    await start_ranging(I2C_ADDR)
    await get_distance(I2C_ADDR, read=False)
    await stop_ranging(I2C_ADDR)

    await writeto_mem(
        I2C_ADDR, VL53L1_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND, b"\x09"
    )  # two bounds VHV
    await writeto_mem(
        I2C_ADDR, 0x0B, b"\x00"
    )  # start VHV from the previous temperature


async def main(mqtt_client):
    # dual_potty = MqttBoolProp(mqtt_client, MQTT_TOPIC_DUAL_POTTY, False, readonly=True)
    exhaust_time = MqttFloatProp(
        mqtt_client, MQTT_TOPIC_EXHAUST_TIME, 30, readonly=True
    )

    if I2C_ADDR in i2c.scan():
        # TODO: alert over MQTT
        print("Unexpected distance sensor on the Qwiic bus!")
        await sleep_ms(1000)

    s1_en.on()
    while I2C_ADDR not in i2c.scan():
        # TODO: alert over MQTT
        await sleep_ms(1000)

    await init_sensor()
    await set_distance_mode(1)
    await set_inter_measurement_ms(15)
    await set_timing_budget_ms(15)

    await start_ranging()

    while True:
        d = await get_distance()
        print(f"pb_exhaust.main: Distance: {d}")
