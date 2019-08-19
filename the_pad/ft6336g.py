import ustruct as struct

DEFAULT_I2C_ADDR = 0x38
REG_DATA = 0x00
REG_NUMTOUCHES = 0x02


class FT6336G:
    """
    Driver for the FT6336G touch panel.
    """
    def __init__(self, i2c, address=DEFAULT_I2C_ADDR):
        self._i2c = i2c
        self._address = address

    @property
    def touched_count(self):
        """
        Current number of touch events.
        :return: 0, 1 or 2
        """
        return self._read(REG_NUMTOUCHES, 1)[0]

    @property
    def touches(self):
        """
        x and y coordinates for touch events. FT6336G supports up to two simultaneous touch events.
        Returns empty list if there is no touch.
        :return: list of (x,y) tuples.
        """
        points = []

        if not self.touched_count:
            return points

        data = self._read(REG_DATA, 32)

        for i in range(2):
            point = data[i * 6 + 3: i * 6 + 9]
            if all([i == 0xFF for i in point]):
                continue
            x, y = struct.unpack('>HH', point)
            x &= 0xFFF
            y &= 0xFFF
            point = (x, y)
            points.append(point)
        return points

    def _read(self, register, length):
        """
        Reads *length* bytes over i2c.
        :param register: byte register
        :param length: number of bytes to read
        :return: filled bytearray
        """
        self._i2c.writeto(self._address, bytes([register & 0xFF]))
        result = bytearray(length)
        self._i2c.readfrom_into(self._address, result)
        return result


def main():
    from machine import Pin, I2C

    i2c = I2C(scl=Pin(27), sda=Pin(32))
    ft6336g = FT6336G(i2c)
    while True:
        print(ft6336g.touches)
