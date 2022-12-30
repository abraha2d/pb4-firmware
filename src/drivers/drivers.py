from uasyncio import sleep_ms

from upy_platform import i2c, s1_en, s2_en

from .constants import BUS_QWIIC, BUS_S1, BUS_S2, ADDRESS_SET

DRIVER_LIST = {}

devices = set()
s1_devices = set()
s2_devices = set()


def register_address(address, name, callback):
    DRIVER_LIST[address] = (name, callback)


def remove_addrs(addrs):
    global devices, s1_devices, s2_devices
    devices -= addrs
    s1_devices -= addrs
    s2_devices -= addrs


def readfrom_mem(addr, memaddr, nbytes, *, addrsize=8):
    try:
        return i2c.readfrom_mem(addr, memaddr, nbytes, addrsize=addrsize)
    except OSError:
        print(f"drivers.readfrom_mem: Lost 0x{addr:02x}")
        remove_addrs({addr})
        raise


def writeto_mem(addr, memaddr, buf, *, addrsize=8):
    try:
        return i2c.writeto_mem(addr, memaddr, buf, addrsize=addrsize)
    except OSError:
        print(f"drivers.writeto_mem: Lost 0x{addr:02x}")
        remove_addrs({addr})
        raise


async def handle_i2c():
    global devices, s1_devices, s2_devices
    while True:
        await sleep_ms(1000)
        scan = set(i2c.scan())

        # Remove devices that aren't connected anymore
        if devices - scan:
            lost_devices = ", ".join(f"0x{d:02x}" for d in (devices - scan))
            print(f"drivers.handle_i2c: Lost {lost_devices}")
            remove_addrs(devices - scan)

        for sX_devices, sX_en, sX_bus in [
            (set(), None, BUS_QWIIC),
            (s1_devices, s1_en, BUS_S1),
            (s2_devices, s2_en, BUS_S2),
        ]:
            if not sX_devices:
                if sX_en is not None:
                    # Enable sensor X power to check for new connections
                    sX_en.on()
                    await sleep_ms(1)
                    sX_scan = set(i2c.scan()) - scan
                else:
                    sX_scan = scan

                # Add devices that were just connected
                for d in sX_scan - devices:
                    if d in DRIVER_LIST.keys():
                        drv_name, drv_callback = DRIVER_LIST[d]
                        print(f"drivers.handle_i2c: {sX_bus}/0x{d:02x} => {drv_name}")
                        open_addrs = (ADDRESS_SET - set(DRIVER_LIST.keys())) - devices

                        try:
                            new_d = await drv_callback(sX_bus, d, open_addrs)
                        except OSError:
                            print(f"drivers.handle_i2c: Device disappeared!")
                            continue

                        if new_d is None:
                            print(f"drivers.handle_i2c: Driver did not handle device!")
                        else:
                            print(f"drivers.handle_i2c: {drv_name} => 0x{new_d:02x}")
                            d = new_d
                    else:
                        print(f"drivers.handle_i2c: {sX_bus}/0x{d:02x} => <no handler>")
                    sX_devices.add(d)
                    devices.add(d)

                if not sX_devices and sX_en is not None:
                    # Nothing is connected, disable sensor X power
                    sX_en.off()
