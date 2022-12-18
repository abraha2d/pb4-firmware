from time import ticks_ms, ticks_diff

from uasyncio import sleep_ms

from mqtt.property import MqttBoolProp, MqttFloatProp
from upy_platform import (
    exhaust,
    i2c,
    s1_en,
    s1_led,
    s2_en,
    s2_led,
)
from .config import (
    I2C_ADDR,
    MQTT_TOPIC_DUAL_POTTY,
    MQTT_TOPIC_EXHAUST_TIME,
)
from .vl53l1_config import DEFAULT_CONFIG
from .vl53l1_register_map import (
    VL53L1_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND,
    GPIO__TIO_HV_STATUS,
    SYSTEM__INTERRUPT_CLEAR,
    SYSTEM__MODE_START,
    VL53L1_RESULT__FINAL_CROSSTALK_CORRECTED_RANGE_MM_SD0,
    VL53L1_FIRMWARE__SYSTEM_STATUS,
)


async def start_sensor(i2c_addr=I2C_ADDR):
    i2c.writeto_mem(i2c_addr, SYSTEM__MODE_START, 0x40)


async def get_distance(i2c_addr=I2C_ADDR):
    while True:
        await sleep_ms(1)
        d = i2c.readfrom_mem(i2c_addr, GPIO__TIO_HV_STATUS, 1)
        if d & 1:
            break
    d = i2c.readfrom_mem(i2c_addr, VL53L1_RESULT__FINAL_CROSSTALK_CORRECTED_RANGE_MM_SD0, 2)
    i2c.writeto_mem(i2c_addr, SYSTEM__INTERRUPT_CLEAR, 0x01)
    return d


async def stop_sensor(i2c_addr=I2C_ADDR):
    i2c.writeto_mem(i2c_addr, SYSTEM__MODE_START, 0x00)


async def init_sensor():
    # Wait for device booted
    while True:
        await sleep_ms(1)
        d = i2c.readfrom_mem(I2C_ADDR, VL53L1_FIRMWARE__SYSTEM_STATUS, 1)
        if d[0] & 0x01:
            break

    # Sensor init
    i2c.writeto_mem(I2C_ADDR, 0x2D, DEFAULT_CONFIG)
    await get_distance(I2C_ADDR)
    await stop_sensor(I2C_ADDR)
    i2c.writeto_mem(I2C_ADDR, VL53L1_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND, 0x09)  # two bounds VHV
    i2c.writeto_mem(I2C_ADDR, 0x0B, 0)  # start VHV from the previous temperature
    await start_sensor(I2C_ADDR)


async def main(mqtt_client):
    # dual_potty = MqttBoolProp(mqtt_client, MQTT_TOPIC_DUAL_POTTY, False, readonly=True)
    exhaust_time = MqttFloatProp(mqtt_client, MQTT_TOPIC_EXHAUST_TIME, 30, readonly=True)

    s1_en.off()
    s2_en.off()

    if I2C_ADDR in i2c.scan():
        # TODO: alert over MQTT
        raise Exception("Unexpected distance sensor on the Qwiic bus!")

    s1_en.on()
    while I2C_ADDR not in i2c.scan():
        # TODO: alert over MQTT
        await sleep_ms(1000)

    await init_sensor()

    while True:
        d = await get_distance()
        print(f"pb_exhaust.main: Distance: {d}")

    # touch_pad = [touch_1, touch_2]
    # touch_avg = [None, None]
    # flush_start = [None, None]
    # flush_sig = [flush_1, flush_2]
    #
    # def process_touch(idx):
    #     try:
    #         touch_val = touch_pad[idx].read()
    #     except ValueError:
    #         return
    #
    #     if touch_avg[idx] is None:
    #         touch_avg[idx] = touch_val
    #
    #     pressed = touch_val < touch_avg[idx] * THRESHOLD
    #
    #     if not pressed:
    #         touch_avg[idx] = (1 - CAL_ALPHA) * touch_avg[idx] + CAL_ALPHA * touch_val
    #     elif flush_start[idx] is None:
    #         flush_start[idx] = ticks_ms()
    #
    #     flush_val = pressed or (
    #             flush_start[idx] is not None and
    #             ticks_diff(ticks_ms(), flush_start[idx]) < flush_time.get() * 1000
    #     )
    #
    #     if not flush_val:
    #         flush_start[idx] = None
    #
    #     flush_sig[idx].value(flush_val)
    #     print(f"Touch {idx}: {touch_val}\tavg: {touch_avg[idx]:.3f}\tpress: {pressed}\tflush: {flush_val}")
    #
    # while True:
    #     process_touch(0)
    #     if dual_potty.get():
    #         process_touch(1)
    #     await sleep_ms(LOOP_TIME)
