from .panels import TablePanel, QRCodePanel
from .screen import Screen
from . import arial20 as font


class Writer:
    def __init__(self, screen=None):
        if screen is None:
            screen = Screen()
        self.screen = screen
        self.font = font
        
    def display(self):
        self.screen.display()
        
    def text(self, text, x, y, scale=1, color=None):
        if color is None:
            color = self.screen.black
        current_x = x
        height = self.font.height()
        reverse = self.font.reverse()
        
        for char in text:
            try:
                result = self.font.get_ch(char)
            except (AttributeError, KeyError):
                result = self.font.get_ch(' ')
            
            glyph, _, width = result
            
            bytes_per_row = (width - 1)//8 + 1
            for row in range(height):
                for col in range(width):
                    byte = glyph[row * bytes_per_row + col // 8]
                    if reverse:
                        bit = (byte & (1 << (col % 8))) > 0
                    else:
                        bit = (byte & (1 << (7 - (col % 8)))) > 0
                    if bit:
                        if scale == 1:
                            self.screen.frame.pixel(current_x + col, y + row, color)
                        else:
                            self.screen.frame.fill_rect(
                                current_x + (col * scale),
                                y + (row * scale),
                                scale, scale, color
                            )
            current_x += width * scale
            
    def panel(self, panel):
        self.screen.frame.fill_rect(
            panel.x,
            panel.y,
            panel.width,
            panel.height,
            self.screen.white
        )
        if isinstance(panel, TablePanel):
            x = panel.x
            y = panel.y
            dy = int(1.2 * self.font.height())
            for i, line in enumerate(panel.lines):
                if i == 0:
                    self.text(line[0], x, y)
                _x = x
                for j, text in enumerate(line):
                    self.text(text, _x, y)
                    _x += panel.config['column_widths'][j]
                y += dy
        elif isinstance(panel, QRCodePanel):
            if panel.matrix is None:
                return
            x = panel.x
            y = panel.y
            scale = panel.scale
            for i, line in enumerate(panel.matrix):
                for j, value in enumerate(line):
                    if value:
                        if scale == 1:
                            self.screen.frame.pixel(x + i, y + j, self.screen.black)
                        else:
                            self.screen.frame.fill_rect(
                                x + scale * i,
                                y + scale * j,
                                scale,
                                scale,
                                self.screen.black
                            )
        
if __name__ == "__main__":
    writer = Writer()
    writer.text("Hello World!", 340, 220)
    writer.text("Pico 2 W + Waveshare 7.5 E-Paper", 260, 250)
    writer.display()
        