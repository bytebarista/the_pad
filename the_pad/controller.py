"""
High level access to buttons, thumb stick and .
"""
from machine import Pin, ADC


class ThumbStick(object):
    ADC_RANGE = 4096

    def __init__(self, discreet_threshold=0.7):
        if (discreet_threshold <= 0) or (discreet_threshold >= 1.0):
            raise ValueError(
                'discreet_threshold = %0.3f must be > 0 and <= 1'
                % discreet_threshold
            )
        self.discreet_threshold = discreet_threshold
        self.access_x = ADC(Pin(34))
        self.access_x.atten(ADC.ATTN_11DB)
        self.access_x.width(ADC.WIDTH_12BIT)

        self.access_y = ADC(Pin(39))
        self.access_y.atten(ADC.ATTN_11DB)
        self.access_y.width(ADC.WIDTH_12BIT)

    def x_raw(self):
        return self._raw(self.access_x)

    def y_raw(self):
        return self._raw(self.access_y)

    def _raw(self, access):
        return int(access.read() * 256 / ThumbStick.ADC_RANGE)

    def x(self):
        """
        Normalized horizontal position ranging from -1.0 to 1.0.
        """
        return self._normalized(self.access_x)

    def y(self):
        """
        Normalized vertical position ranging from -1.0 to 1.0.
        """
        return self._normalized(self.access_y)

    def _normalized(self, access):
        """
        Value between 0 and ThumbStick.ADC_RANGE - 1 normalized to range -1.0 and 1.0.
        """
        return (access.read() - 2047.5) / 2047.5


thumbstick = ThumbStick()
