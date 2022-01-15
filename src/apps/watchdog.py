from machine import WDT
from uasyncio import sleep_ms

NAME = "Watchdog"


async def main(mqtt_client):
    # TODO: get config from MQTT
    feed_time = 1000
    bite_time = 60000
    print(f"apps.watchdog.main: Watchdog bites at {bite_time} ms, feeding at {feed_time} ms.")

    wdt = WDT(timeout=bite_time)
    print(f"apps.watchdog.main: Started Watchdog.")

    while True:
        wdt.feed()
        await sleep_ms(feed_time)
