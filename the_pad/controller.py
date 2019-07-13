"""
High level access to buttons, thumb stick and .
"""
import mcpnew
from machine import Pin, ADC
from the_pad import pins

#: Maximum discreet value from ADC.
MAX_RAW_VALUE = 4096

#: Factor to normalize values from ADC to range between -1.0 and 1.0.
_RAW_NORMALIZER = (MAX_RAW_VALUE / 2) - 0.5


#: Factor to convert original output from ADC to int value between 0 and MAX_RAW_VALUE.
_RAW_FACTOR = 256 / MAX_RAW_VALUE


class ThumbSlide(object):

    def __init__(self, discreet_threshold=0.7):
        if (discreet_threshold <= 0) or (discreet_threshold >= 1.0):
            raise ValueError(
                'discreet_threshold = %0.3f must be > 0 and <= 1'
                % discreet_threshold
            )
        self.discreet_threshold = discreet_threshold
        self.access_x = ADC(Pin(pins.THUMBSLIDE_X))
        self.access_x.atten(ADC.ATTN_6DB)
        self.access_x.width(ADC.WIDTH_12BIT)
        self.access_y = ADC(Pin(pins.THUMBSLIDE_Y))
        self.access_y.atten(ADC.ATTN_6DB)
        self.access_y.width(ADC.WIDTH_12BIT)

    @property
    def x_raw(self):
        return self._raw(self.access_x)

    @property
    def y_raw(self):
        return self._raw(self.access_y)

    def _raw(self, access):
        return int(access.read() * _RAW_FACTOR)

    @property
    def x(self):
        """
        Normalized horizontal position ranging from -1.0 to 1.0.
        """
        return self._normalized(self.access_x)

    @property
    def y(self):
        """
        Normalized vertical position ranging from -1.0 to 1.0.
        """
        return self._normalized(self.access_y)

    def _normalized(self, access):
        """
        Value between 0 and ThumbStick.ADC_RANGE - 1 normalized to range -1.0 and 1.0.
        """
        return (access.read() - _RAW_NORMALIZER) / _RAW_NORMALIZER

    @property
    def is_up(self):
        return self.y > self.discreet_threshold

    @property
    def is_down(self):
        return self.y < self.discreet_threshold

    @property
    def is_left(self):
        return self.x < self.discreet_threshold

    @property
    def is_right(self):
        return self.x > self.discreet_threshold

class Buttons:
    """Controller class for the 4 buttons on the right hand side.

    Parameters
    ----------
    io_handler: mcpnew.MCP
        Handles signals from the buttons. If `None`, it will automatically be
        assigned to the default.

    """

    BUTTON_LEFT = 5
    BUTTON_RIGHT = 6
    BUTTON_UP = 7
    BUTTON_DOWN = 4
    PINS = [BUTTON_LEFT, BUTTON_RIGHT, BUTTON_UP, BUTTON_DOWN]

    def __init__(self, io_handler=None):
        self.io_handler = io_handler
        self._setup()

    def _setup(self):
        if self.io_handler is None:
            i2c = I2C(scl=Pin(pins.I2C_SCL), sda=Pin(pins.I2C_SDA))
            self.io_handler = mcpnew.MCP23017(i2c)

        for pin in self.PINS:
            self.io_handler.setup(pin, mcpnew.IN)
            self.io_handler.pullup(pin, True)

    @property
    def up(self):
        """Check if the up button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.BUTTON_UP)

    @property
    def down(self):
        """Check if the down button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.BUTTON_DOWN)

    @property
    def right(self):
        """Check if the right button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.BUTTON_RIGHT)

    @property
    def left(self):
        """Check if the left button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.BUTTON_LEFT)

    def get_all(self):
        """Get all buttons that are pressed.

        Returns
        -------
        list of str
            With all the buttons that where pressed.

        """
        buttons = []

        if self.up:
            buttons.append('UP')
        if self.down:
            buttons.append('DOWN')
        if self.right:
            buttons.append('RIGHT')
        if self.left:
            buttons.append('LEFT')

        return buttons

