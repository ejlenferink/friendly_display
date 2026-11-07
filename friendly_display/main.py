import json
import os
import time
TIMEZONE_OFFSET = -4

from .mbta_client import MBTAClient
from .queriers import TransitGroupQuerier
from .panels import TransitPanel

import hardware_setup  # Must be first: creates the display

import asyncio
from gui.core.ugui import Screen, ssd
from gui.core.writer import Writer  # Monochrome display: Writer, not CWriter
from gui.widgets import Label, Button, CloseButton, QRMap
import gui.fonts.arial20 as font10
from gui.core.colors import BLACK, WHITE

ssd.min_interval = 5_000  # ms between refreshes. 0 = refresh on every change.


class BaseScreen(Screen):
    def __init__(self, panels=[], interval_seconds=1):
        super().__init__()
        wri = Writer(ssd, font10, verbose=False)
        super().__init__(wri)
        self.wri = wri
        self.n = 0
        self.interval_seconds = interval_seconds
        self.panels = panels
        
        column_widths = [300, 150, 330]
        column_offsets = []
        total = 0
        for width in column_widths:
            column_offsets.append(total)
            total += width
        self.max_items = 5
        
        self.display_panels = []
        
        x0, y0 = 10, 10
        self.display_panels.append({
            "header": Label(wri, y0, x0, total),
            "lines": [
                [
                    Label(wri, y0 + 24*(i + 1), x0 + _, __) for _, __ in zip(column_offsets, column_widths)
                ] for i in range(self.max_items)
            ]
        })
        
        y0 += int((self.max_items + 2.5) * 24) 
        self.display_panels.append({
            "header": Label(wri, y0, x0, total),
            "lines": [
                [
                    Label(wri, y0 + 24*(i + 1), x0 + _, __) for _, __ in zip(column_offsets, column_widths)
                ] for i in range(self.max_items)
            ]
        })
        
        y0 = 386
        self.qrcode = QRMap(wri, y0, x0, version=4, scale=2)
        self.qrcode.fgcolor=WHITE
        self.qrcode.bgcolor=BLACK
        self.qrcode.value("WIFI:S:Poopycat 2.4G;T:WPA;P:iamaleafonthewind;H:false;;")
        
        self.display_time = Label(wri, y0, 2*x0 + 94, 200)
        
    def after_open(self):  # Runs once the screen is up and asyncio is running
        self.reg_task(self.updater())  # Task is cancelled automatically on close

    async def updater(self):
        # Stand-in for "fetch bus times". Change the label whenever you like;
        # the driver batches changes into one refresh per min_interval.
        while True:
            await asyncio.sleep(self.interval_seconds)
            self.n += 1
            for panel, display_panel in zip(self.panels, self.display_panels):
                panel.refresh()
                lines, colors = panel.render()
                display_panel["header"].value(lines[0][0])
                for i, line in enumerate(lines[1:self.max_items+1]):
                    for j, text in enumerate(line):
                        display_panel["lines"][i][j].value(text)
                        
            now = time.localtime(time.time() + TIMEZONE_OFFSET * 3600)
            text = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(*now[:6])
            self.display_time.value(text)


class DashboardEngine:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = 'friendly_display/config.json'
        with open(config_path) as f:
            config = json.load(f)

        settings = config["mbta_settings"]
        self.client = MBTAClient(base_url=settings["base_url"], api_key=settings.get("api_key"))

        self.panels = []
        for group_name, rules in config["transit_groups"].items():
            querier = TransitGroupQuerier(self.client, rules["stops"], rules.get("routes"))
            self.panels.append(TransitPanel(group_name, querier))

    def run_forever(self, interval_seconds=30):
        Screen.change(BaseScreen, kwargs={"interval_seconds": interval_seconds, "panels": self.panels})

if __name__ == "__main__":
    engine = DashboardEngine()
    engine.run_forever(interval_seconds=15)
