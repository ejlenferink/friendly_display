from machine import Pin, SPI
import framebuf
import time
from . import arial20 as font

WIDTH = 800
HEIGHT = 480

RESET_PIN = 12
DC_PIN = 8
CS_PIN = 9
BUSY_PIN = 13

SCK_PIN = 10
MOSI_PIN = 11
MISO_PIN = 28

class Screen:
    def __init__(self):
        
        self.reset_pin = Pin(RESET_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        self.width = WIDTH
        self.height = HEIGHT
        
        self.white = 0x00
        self.black = 0xff
        
        self.font = font
        
        self.spi = SPI(1, 
                       baudrate=4000000, 
                       polarity=0, 
                       phase=0, 
                       sck=Pin(SCK_PIN), 
                       mosi=Pin(MOSI_PIN), 
                       miso=Pin(MISO_PIN))
        #self.spi = SPI(1)
        #self.spi.init(baudrate=4000_000)
        
        self._frame = bytearray(self.height * self.width // 8)
        self.frame = framebuf.FrameBuffer(self._frame, self.width, self.height, framebuf.MONO_HLSB)
        self.frame.fill(self.white)
        self.init()
        
    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()
        
    def delay_ms(self, delaytime):
        time.sleep_ms(int(delaytime))
        
    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytes([command]))
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytes([data & 0xFF]))
        self.digital_write(self.cs_pin, 1)
        
    def wait_until_idle(self):
        while(self.digital_read(self.busy_pin) == 0):
            self.send_command(0x71)
            self.delay_ms(20)
        
    def init(self):
        self.reset()
        
        self.send_command(0x06)
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x28)        
        self.send_data(0x17)
        
        self.send_command(0x01)
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x28)
        self.send_data(0x17)

        self.send_command(0x04)
        self.delay_ms(100)
        self.wait_until_idle()

        self.send_command(0X00)
        self.send_data(0x1F)   

        self.send_command(0x61)
        self.send_data(0x03)
        self.send_data(0x20)
        self.send_data(0x01)
        self.send_data(0xE0)

        self.send_command(0X15)
        self.send_data(0x00)

        self.send_command(0X50)
        self.send_data(0x10)
        self.send_data(0x07)

        self.send_command(0X60)
        self.send_data(0x22)
        
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)
        
    def display(self):
        self.send_command(0x13) 
        chunk_size = 4096
        total_size = len(self._frame)
        
        self.digital_write(self.dc_pin, 1)
        for i in range(0, total_size, chunk_size):
            chunk = memoryview(self._frame)[i : i + chunk_size]
            self.digital_write(self.cs_pin, 0)
            self.spi.write(chunk)
            self.digital_write(self.cs_pin, 1)
            
        self.send_command(0x12)
        self.delay_ms(100)      
        self.wait_until_idle()
        
    def text(self, text, x, y, scale=1, color=None):
        if color is None:
            color = self.black
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
                            self.frame.pixel(current_x + col, y + row, color)
                        else:
                            self.frame.fill_rect(
                                current_x + (col * scale),
                                y + (row * scale),
                                scale, scale, color
                            )
            current_x += width * scale
        
if __name__ == "__main__":
    screen = Screen()
    screen.text("Hello Wdfsdsfdsforld!", 340, 220)
    screen.text("Pico 2 W + Waveshare 7.5 E-Paper", 260, 250)
    screen.display()
        