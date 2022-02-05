from uasyncio import create_task


class MqttProp:
    def __init__(
            self,
            client,
            topic,
            default=None,
            qos=2,
            retain=True,
            readonly=False,
            writeonly=False,
    ):
        self.client = client
        self.topic = topic
        self.df = default
        self.qos = qos
        self.retain = retain
        self.readonly = readonly
        self.writeonly = writeonly

        self.data = None
        if not self.writeonly:
            # TODO: Handle multiple properties on same topic
            print(f"mqtt.property: {self.topic} -> ?")
            create_task(self.client.subscribe((self.topic, self.qos, self.recv_data)))

    @staticmethod
    def default():
        return b""

    @staticmethod
    def htond(data):
        return str(data).encode()

    @staticmethod
    def ntohd(data):
        return bytes(data)

    # noinspection PyUnusedLocal
    async def recv_data(self, client, topic, data, retained):
        if self.writeonly:
            print(f"mqtt.property: WARNING: Ignoring update to a write-only property: {self.topic}")
        else:
            print(f"mqtt.property: {self.topic} -> ", end="")
            self.data = self.ntohd(data)
            print(self.data)

    def get(self):
        default = self.default() if self.df is None else self.df
        return default if self.data is None else self.data

    def set(self, data):
        if self.readonly:
            print(f"mqtt.property: WARNING: Ignoring update to a read-only property: {self.topic}")
        elif self.data != data:
            self.data = data
            create_task(self.client.publish(self.topic, self.htond(data), self.qos, self.retain, ))


class MqttFloatProp(MqttProp):
    @staticmethod
    def default():
        return 0.0

    @staticmethod
    def ntohd(data):
        return float(bytes(data))


class MqttIntProp(MqttProp):
    @staticmethod
    def default():
        return 0

    @staticmethod
    def ntohd(data):
        return int(float(bytes(data)))


class MqttBoolProp(MqttProp):
    @staticmethod
    def default():
        return False

    @staticmethod
    def htond(data):
        return b"1" if data else b"0"

    @staticmethod
    def ntohd(data):
        return bool(int(float(bytes(data))))
