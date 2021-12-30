# noinspection PyUnresolvedReferences
from webrepl import accept_conn, setup_conn

NAME = "WebREPL"


async def main(mqtt_client):
    # TODO: get config from MQTT
    port = 8266

    setup_conn(port, accept_conn)
    print(f"apps.webrepl.main: Started WebREPL.")
