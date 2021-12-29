from binascii import hexlify

from uasyncio import sleep_ms

from upy_platform import ds


async def main():
    while True:
        roms = ds.scan()
        ds.convert_temp()
        sleep_ms(750)
        for rom in sorted(roms):
            try:
                t = ds.read_temp(rom)
                print(f"{hexlify(rom)}: {t}")
            except Exception:
                pass
        print()
