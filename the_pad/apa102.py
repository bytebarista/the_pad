class APA102:

    #XXX not used yet - do we need it? See micropython code for ESP8266.
    ORDER = (0, 1, 2, 3)

    leds = []

    def __init__(self, spi, n=4):
        self.spi = spi
        self.spi.init(baudrate=4000000)
        self.n = n
        # init led value matrix
        for i in range(n):
            self.leds.append([0, 0, 0, 0])

    def __setitem__(self, index, color):
        # color is 4d array (last item is brightness)
        # brightness is 5Bit
        if not (0 <= color[3] <= 31):
            raise ValueError("Invalid brightness! 0(off) to 31(full)")
        self.leds[index] = color

    def __getitem__(self, index):
        return self.leds[index]

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
        # TODO: set `leds` to zero
        self._start_frame()
        for i in range(4):
            self._send_byte(bytearray([0xE0] + [0] * 3))
        self._end_frame()

    def _send_single(self, color):
        # default: color is 4d array (last item is brightness)
        self._send_byte(bytearray([0xE0 + color[3]] + [color[2]] + [color[1]] + [color[0]]))

    def write(self):
        self._start_frame()

        for i in range(len(self.leds)):
            self._send_single(self.leds[i])

        self._end_frame()
