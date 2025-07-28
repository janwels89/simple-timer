# Mocks for testing

class WaveI2COLED:
    def __init__(self, width=128, height=64, i2c_address=0x3C):
        self.width = width
        self.height = height
        self.i2c_address = i2c_address
        self.buffer = []  # store drawn text lines

    def clear(self):
        self.buffer.clear()
        print(f"[WaveI2COLED] Screen cleared ({self.width}x{self.height})")

    def text(self, message, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer.append({'text': message, 'x': x, 'y': y})
            print(f"[WaveI2COLED] Text '{message}' at ({x},{y})")
        else:
            print(f"[WaveI2COLED] WARNING: Text position ({x},{y}) outside screen!")

    def show(self):
        print("[WaveI2COLED] Display content:")
        for item in self.buffer:
            print(f"  '{item['text']}' at ({item['x']},{item['y']})")

    @property
    def last_text(self):
        # Combine all texts into one string for easy test checking
        return " ".join(item['text'] for item in self.buffer)