from friendly_display.main import DashboardEngine
from secrets import WIFI_PASSWORD, WIFI_SSID
import network
import ntptime
import time

# Initialize Wi-Fi interface in station mode
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Connect to the Wi-Fi network
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
# Wait for the connection to establish
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Check connection status
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected!')
    print('ip address:', wlan.ifconfig()[0])

ntptime.settime()

#ih.network_connect(WIFI_SSID, WIFI_PASSWORD)

#inky_frame.set_time()
#inky_frame.pcf_to_pico_rtc()

engine = DashboardEngine()
engine.run_forever()