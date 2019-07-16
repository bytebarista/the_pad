from machine import SPI, Pin, I2C

import pins
import ili934xhax

__all__ = ['setup']

DEFAULT_RES = (240, 320)
DEFAULT_BACKGROUND = (0, 0, 0)


def setup(res=None, background=None, framebuf=False, write_only=True):
    """Initiate and setup the pad's display.

    Parameters
    ----------
    res: tuple
        Represents the resolution of the screen, as a (width, height) tuple.
        If `None`, it will use a default value. Default `None`.
    background: tuple
        Represents the initial background color of the screen, as a (r, g, b)
        tuple. If `None`, it will default to (0, 0, 0). Default `None`.
    framebuf: bool
        Whether the micropython's framebuf module is in use or not. Default
        `False`.
    write_only: bool
        Whether the screen is supposed to be write-only or not. Default `True`.

    Returns
    -------
    ili934xhax.ILI9341
        With the configured display.

    """
    if res is None:
        res = DEFAULT_RES

    if background is None:
        background = DEFAULT_BACKGROUND

    if framebuf:
        color_fn = ili934xhax.color565
    else:
        color_fn = ili934xhax.color565n
    if not write_only:
        spi = SPI(2, baudrate=40000000, miso=Pin(pins.SPI_MISO),
                  mosi=Pin(pins.SPI_MOSI), sck=Pin(pins.SPI_CLK))
    else:
        spi = SPI(2, baudrate=40000000, mosi=Pin(pins.SPI_MOSI),
                  sck=Pin(pins.SPI_CLK))

    display = ili934xhax.ILI9341(spi, cs=Pin(0), dc=Pin(15), rst=Pin(5))

    display.erase()
    display.set_pos(0, 0)
    display.width = res[0]
    display.height = res[1]

    display.fill_rectangle(0, 0, res[0], res[1], color_fn(*background))

    return display
