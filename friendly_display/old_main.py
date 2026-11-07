"""
Entry point. DashboardEngine reads config.json, builds one TransitPanel
per transit group, and runs the refresh/print loop.

Nothing here mentions Harvard, Watertown, 71, or 73 -- that all lives in
config.json.
"""

import framebuf
import json
import os
import time
TIMEZONE_OFFSET = -4

from .mbta_client import MBTAClient
from .queriers import TransitGroupQuerier
from .panels import TransitPanel
from . import Pico_ePaper_7_5
from .font_writer import CustomFontWriter
from . import arial20

def scaled_text(fbuf, text, x, y, scale, color):
    # Each character is natively 8 pixels wide
    for char_idx, char in enumerate(text):
        # Create a temporary 8x8 buffer to render a single character
        char_buf = bytearray(8)
        char_fbuf = framebuf.FrameBuffer(char_buf, 8, 8, framebuf.MONO_VLSB)
        char_fbuf.text(char, 0, 0, 1)
        
        # Scale and copy pixels over to the main frame buffer
        for px in range(8):
            for py in range(8):
                if char_fbuf.pixel(px, py):
                    # Draw a scaled block for each active pixel
                    fbuf.fill_rect(
                        x + (char_idx * 8 * scale) + (px * scale),
                        y + (py * scale),
                        scale, scale, color
                    )


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
            
        self.epd = Pico_ePaper_7_5.EPD_7in5()
        self.canvas = self.epd.image1Gray
        self.font_writer = CustomFontWriter(self.canvas, arial20)

    def run_forever(self, interval_seconds=20):
        scale = 1
        cell_widths = [300, 150, 350]
        while True:
            start = time.time()
            self.canvas.fill(0xff)           
            #graphics.set_font('bitmap8')
            xoffset = 10
            yoffset = 10
            for panel in self.panels:
                panel.refresh()
                lines, colors = panel.render()
                y = yoffset
                for line, color in zip(lines, colors):
                    #graphics.set_pen(getattr(inky_frame, color.upper()))
                    x = xoffset
                    for j, text in enumerate(line):
                        self.font_writer.write_text(text, x, y)
                        #scaled_text(self.canvas, text, x, y, 2, 0x00)
                        #self.canvas.text(text, x, y, 0x00)
                        #graphics.text(text, x, y, 800-xoffset, scale=scale)
                        x += cell_widths[j]
                    y += scale*25
                yoffset += 240
            #graphics.update()
            
            now = time.localtime(time.time() + TIMEZONE_OFFSET * 3600)
            text = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(*now[:6])
            self.font_writer.write_text(text, xoffset, 480 - xoffset - 25)
            #print(time.time()-start)
                
                
            self.epd.display(self.epd.buffer_1Gray)
            time.sleep(interval_seconds)


if __name__ == "__main__":
    engine = DashboardEngine()
    engine.run_forever(interval_seconds=15)
