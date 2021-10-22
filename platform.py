print("===IMPORTING platform.py===")
import network
import esp32

wlan_sta = network.WLAN(network.STA_IF)
wlan_ap = network.WLAN(network.AP_IF)
nvs = esp32.NVS("pb4")
