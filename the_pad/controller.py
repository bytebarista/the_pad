"""
High level access to buttons, thumb stick and .
"""
import mcpnew
from machine import Pin, ADC, I2C
from the_pad import pins


__all__ = ['ThumbSlide', 'DPad', 'Buttons',
           'configure_directional_controllers']


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


class BaseButtonController:

    PINS = []

    def __init__(self, io_handler=None):
        self.io_handler = _setup_io(io_handler, self.PINS)

    @property
    def is_up(self):
        raise NotImplementedError()

    @property
    def is_down(self):
        raise NotImplementedError()

    @property
    def is_right(self):
       raise NotImplementedError()

    @property
    def is_left(self):
        raise NotImplementedError()

    def get_all(self):
        """Get all buttons that are pressed.

        Returns
        -------
        set of str
            With all the buttons that where pressed.

        """
        buttons = set()

        if self.is_up:
            buttons.add('UP')
        if self.is_down:
            buttons.add('DOWN')
        if self.is_right:
            buttons.add('RIGHT')
        if self.is_left:
            buttons.add('LEFT')

        return buttons


class Buttons(BaseButtonController):
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

    @property
    def is_up(self):
        """Check if the up button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.BUTTON_UP)

    @property
    def is_down(self):
        """Check if the down button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.BUTTON_DOWN)

    @property
    def is_right(self):
        """Check if the right button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.BUTTON_RIGHT)

    @property
    def is_left(self):
        """Check if the left button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.BUTTON_LEFT)


class DPad(BaseButtonController):

    PIN_LEFT = 9
    PIN_RIGHT = 10
    PIN_UP = 8
    PIN_DOWN = 11
    PINS = [PIN_LEFT, PIN_RIGHT, PIN_UP, PIN_DOWN]

    @property
    def is_up(self):
        """Check if the up button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.PIN_UP)

    @property
    def is_down(self):
        """Check if the down button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.PIN_DOWN)

    @property
    def is_right(self):
        """Check if the right button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.PIN_RIGHT)

    @property
    def is_left(self):
        """Check if the left button is pressed.

        Returns
        -------
        bool
            Whether the button is pressed or not.

        """
        return not self.io_handler.input(self.PIN_LEFT)


def _setup_io(io_handler, use_pins):
    if io_handler is None:
        i2c = I2C(scl=Pin(pins.I2C_SCL), sda=Pin(pins.I2C_SDA))
        io_handler = mcpnew.MCP23017(i2c)

    for pin in use_pins:
        io_handler.setup(pin, mcpnew.IN)
        io_handler.pullup(pin, True)

    return io_handler


def configure_directional_controllers(io_handler=None, discreet_threshold=0.7):
    """Configure all directional controllers.

    Parameters
    ----------
    io_handler: mcpnew.MCP
        The MCP I/O handler used by the buttons. If `None`, it will be
        configured automatically using the defaults. Default `None`.
    discreet_threshold: float
        Threshold value used by the thumbslide

    Returns
    -------
    ThumbSlide
    Buttons
    DPad
        All with the appropriate configurations.

    """

    thumbslide = ThumbSlide(discreet_threshold)
    buttons = Buttons(io_handler)
    dpad = DPad(buttons.io_handler)

    return thumbslide, buttons, dpad
