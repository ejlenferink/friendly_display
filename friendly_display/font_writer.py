class CustomFontWriter:
    def __init__(self, fbuf, font_module):
        self.fbuf = fbuf
        self.font = font_module
        
    def get_char_bitmap(self, char):
        try:
            return self.font.get_ch(char)
        except (AttributeError, KeyError):
            return self.font.get_ch(' ')

    def write_text(self, text, x, y, scale=1, color=0):
        current_x = x
        height = self.font.height()
        reverse = self.font.reverse()
        
        for char in text:
            # Safely grab the raw layout tuple from the font module
            result = self.get_char_bitmap(char)
            
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
                            self.fbuf.pixel(current_x + col, y + row, color)
                        else:
                            self.fbuf.fill_rect(
                                current_x + (col * scale),
                                y + (row * scale),
                                scale, scale, color
                            )
            current_x += width * scale
                

