"""
Entry point. DashboardEngine reads config.json, builds one TransitPanel
per transit group, and runs the refresh/print loop.

Nothing here mentions Harvard, Watertown, 71, or 73 -- that all lives in
config.json.
"""
import inky_frame
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_SPECTRA_7 as DISPLAY

import json
import os
import time
#from datetime import datetime

from .mbta_client import MBTAClient
from .queriers import TransitGroupQuerier
from .panels import TransitPanel


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

    def run_forever(self, interval_seconds=40):
        graphics = PicoGraphics(DISPLAY)
        scale = 2
        cell_widths = [300, 150, 350]
        while True:
            graphics.set_pen(inky_frame.WHITE)
            graphics.clear()           
            graphics.set_font('bitmap8')
            xoffset = 10
            yoffset = 10
            for panel in self.panels:
                panel.refresh()
                lines, colors = panel.render()
                y = yoffset
                for line, color in zip(lines, colors):
                    graphics.set_pen(getattr(inky_frame, color.upper()))
                    x = xoffset
                    for j, text in enumerate(line):
                        graphics.text(text, x, y, 800-xoffset, scale=scale)
                        x += cell_widths[j]
                    y += scale*10
                yoffset += 240
            graphics.update()
            time.sleep(interval_seconds)


if __name__ == "__main__":
    engine = DashboardEngine()
    engine.run_forever(interval_seconds=15)
