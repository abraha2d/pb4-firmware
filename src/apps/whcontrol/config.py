from config import MQTT_APPS_BASE

MQTT_WHCONTROL_BASE = f"{MQTT_APPS_BASE}/whcontrol"

MQTT_TOPIC_SENSOR_ID_TOP = f"{MQTT_WHCONTROL_BASE}/config/sensor_ids/top"
MQTT_TOPIC_SENSOR_ID_BOTTOM = f"{MQTT_WHCONTROL_BASE}/config/sensor_ids/bottom"

MQTT_TOPIC_HEAT_CUTOFF_CONDENSATION = f"{MQTT_WHCONTROL_BASE}/config/heat/cutoff_condensation"
MQTT_TOPIC_HEAT_CUTOFF_SAFETY = f"{MQTT_WHCONTROL_BASE}/config/heat/cutoff_safety"
MQTT_TOPIC_HEAT_MAX_RUNTIME = f"{MQTT_WHCONTROL_BASE}/config/heat/max_runtime"

MQTT_TOPIC_IGNITER_CHECK_DELAY = f"{MQTT_WHCONTROL_BASE}/config/igniter/check_delay"
MQTT_TOPIC_IGNITER_CHECK_THRESHOLD = f"{MQTT_WHCONTROL_BASE}/config/igniter/check_threshold"
MQTT_TOPIC_IGNITER_COOLOFF_DELAY = f"{MQTT_WHCONTROL_BASE}/config/igniter/cooloff_delay"

MQTT_TOPIC_HEAT_OVERRIDE = f"{MQTT_WHCONTROL_BASE}/input/override"
MQTT_TOPIC_HEAT_SETPOINT = f"{MQTT_WHCONTROL_BASE}/input/setpoint"

MQTT_TOPIC_ALERT_MISSING_SENSOR = f"{MQTT_WHCONTROL_BASE}/alerts/missing_sensor"
MQTT_TOPIC_ALERT_CONDENSATION_CUTOFF = f"{MQTT_WHCONTROL_BASE}/alerts/condensation_cutoff"
MQTT_TOPIC_ALERT_SAFETY_CUTOFF = f"{MQTT_WHCONTROL_BASE}/alerts/safety_cutoff"
MQTT_TOPIC_ALERT_MAX_RUNTIME = f"{MQTT_WHCONTROL_BASE}/alerts/max_runtime"
MQTT_TOPIC_ALERT_IGNITER_CHECK = f"{MQTT_WHCONTROL_BASE}/alerts/igniter_check"

MQTT_TOPIC_OUTPUT_HEAT_ON = f"{MQTT_WHCONTROL_BASE}/output/heat_on"
MQTT_TOPIC_OUTPUT_TEMP_TOP = f"{MQTT_WHCONTROL_BASE}/output/temp_top"
MQTT_TOPIC_OUTPUT_TEMP_BOTTOM = f"{MQTT_WHCONTROL_BASE}/output/temp_bottom"
