from secrets import WIFI_PASSWORD, WIFI_SSID
import network
import ntptime
import time
import json
import gc
from .writer import Writer
from .panels import MBTAPanel, QRCodePanel
from .mbta_client import MBTAClient
try:
    from uQR import QRCode
    uqr_imported = True
except Exception:
    uqr_imported = False

class GUI:
    def __init__(self, config_path=None):
        self.writer = Writer()
        self.panels = []
        
        if config_path is None:
            config_path = 'friendly_display/config.json'
        with open(config_path) as f:
            self.config = json.load(f)
            
        self.tick_seconds = self.config['settings']['global']['tick_seconds']

        self.wlan = None
        self.connect_to_wifi()
        
        _config = self.config['settings']['mbta']
        self.mbta_client = MBTAClient(base_url=_config['base_url'], api_key=_config.get('api_key'))

        self.qr = None
        if uqr_imported:
            self.qr = QRCode(version=4, border=0)

        # Run garbage collection to free up unreferenced memory first
        gc.collect()

        # Get stats in bytes
        free_ram = gc.mem_free()
        allocated_ram = gc.mem_alloc()
        total_ram = free_ram + allocated_ram

        print(f"Free RAM: {free_ram} bytes")
        print(f"Allocated RAM: {allocated_ram} bytes")
        print(f"Total Heap RAM: {total_ram} bytes")
        
        for k, v in self.config["panels"].items():
            cls = {
                'mbta': MBTAPanel,
                'qrcode': QRCodePanel
            }.get(k)
            if cls is not None:
                for _config in v:
                    panel = cls(self, _config)
                    self.panels.append(panel)
                    panel.refresh()
                    self.writer.panel(panel)
                    
        self.writer.display()
        self.run_forever()
                    
    def run_forever(self):
        while True:
            time.sleep(self.tick_seconds)
            any_update = False
            for panel in self.panels:
                update = panel.tick()
                any_update |= update
                if update:
                    panel.refresh()
                    self.writer.panel(panel)
            if any_update:
                self.writer.display()
            
    def connect_to_wifi(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        if not self.wlan.isconnected():
            self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            max_wait = 10
            while max_wait > 0:
                if self.wlan.isconnected():
                    break
                max_wait -= 1
                print('waiting for connection...')
                time.sleep(1)

        if not self.wlan.isconnected() or self.wlan.config('ssid') != WIFI_SSID:
            raise RuntimeError('network connection failed')
        else:
            print('connected!')
            print('ip address:', self.wlan.ifconfig()[0])
        self.wlan.config(pm=network.WLAN.PM_NONE)
        ntptime.settime()
        
    def isconnected_to_wifi(self):
        if self.wlan is None:
            return False
        return wlan.isconnected()
    
if __name__ == "__main__":
    a = GUI()
    print(len(a.panels))
    a.draw()

