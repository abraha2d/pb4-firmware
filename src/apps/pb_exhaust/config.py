from config import MQTT_APPS_BASE

LOOP_TIME = 50

MQTT_POTTYBOX_BASE = f"{MQTT_APPS_BASE}/pottybox"
MQTT_TOPIC_DUAL_POTTY = f"{MQTT_POTTYBOX_BASE}/config/dual_potty"
MQTT_TOPIC_EXHAUST_DELAY = f"{MQTT_POTTYBOX_BASE}/config/exhaust_delay"
MQTT_TOPIC_EXHAUST_TIME = f"{MQTT_POTTYBOX_BASE}/config/exhaust_time"


def get_on_threshold_topic(sensor_bus):
    return f"{MQTT_POTTYBOX_BASE}/config/{sensor_bus}/on_threshold"


def get_off_threshold_topic(sensor_bus):
    return f"{MQTT_POTTYBOX_BASE}/config/{sensor_bus}/off_threshold"
