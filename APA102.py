from machine import Pin, SPI


class APA102:

    values = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]

    def __init__(self, spi, n):
        super().__init__()
        self.spi = spi
        self.spi.init(baudrate=4000000)
        self.n = n

    def __setitem__(self, index, color):
        # color is 4d array (first item is brightness)
        self.values[index] = color
        self.write()

    def __getitem__(self, index):
        return self.values[index]

    def fill(self, color):
        for i in range(self.n):
            self[i] = color

    def _send_byte(self, data):
        self.spi.write(data)

    def _start_frame(self):
        self._send_byte(bytearray([0] * 4))

    def _end_frame(self):
        self._send_byte(bytearray([0xFF] * 4))

    def reset(self):
        # TODO: set `values` to zero
        self._start_frame()
        for i in range(4):
            self._send_byte(bytearray([0xE0] + [0] * 3))
        self._end_frame()

    def _send_single(self, color):
        # color is 4d array (first item is brightness)
        self._send_byte(bytearray([0xE0 + color[0]] + [color[1]] + [color[2]] + [color[3]]))

    def write(self):
        self._start_frame()

        for i in range(len(self.values)):
            self._send_single(self.values[i])

        self._end_frame()


def main():
    led = APA102(SPI(2, sck=Pin(13), mosi=Pin(4), miso=Pin(12)), n=4)
    led[0] = [255, 255, 0, 0]
    led[1] = [255, 0, 255, 0]
    led[2] = [255, 0, 0, 255]
    led[3] = [255, 255, 255, 0]
