from secrets import WIFI_PASSWORD, WIFI_SSID
from .queriers import TransitGroupQuerier


class Panel():
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.ticks = self.config.get('ticks')
        if self.ticks is None:
            self.ticks = 1
        self._tick = self.ticks
        self.scale = self.config.get('scale') or 1
        self.x, self.y = self.config.get('position') or (0, 0)
        self.width, self.height = self.config.get('size') or (100, 100)
        self.name = self.config.get('name') or ""
        
    def tick(self):
        if self.ticks == 0:
            return False
        if self.ticks == 1:
            return True
        self._tick -= 1
        if self._tick <= 0:
            self._tick = self.ticks
            return True
        return False        
        
    def refresh(self, **kwargs):
        pass

    def draw(self, **kwargs):
        pass
    
class QRCodePanel(Panel):
    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.data = f"WIFI:S:{WIFI_SSID};T:WPA;P:{WIFI_PASSWORD};H:false;;"
        self.matrix = None
        qr = self.parent.qr
        if qr is not None:
            qr.clear()
            qr.add_data(self.data)
            self.matrix = qr.get_matrix()
            self.width = len(self.matrix) * self.scale
            self.height = self.width
    
class TablePanel(Panel):
    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.lines = []
        
class MBTAPanel(TablePanel):
    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.mbta_client = self.parent.mbta_client
        self.querier = TransitGroupQuerier(self.mbta_client, config["stops"], config.get("routes"))
        self.max_departures = self.config.get('max_departures') or 5

    def refresh(self):
        self.querier.refresh()
        self.lines = [[f"{self.name.upper()}"]]
        departures = self.querier.get_items()[: self.max_departures]
        if not departures:
            self.lines.append(["No upcoming arrivals scheduled."])
        else:
            for dep in departures:
                line = [
                    f"{dep.route} to {dep.destination}",
                    f"{dep.minutes_away} min",
                    f"{dep.stop_name}"
                ]
                self.lines.append(line)
        
        
        
        
