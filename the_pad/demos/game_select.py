from the_pad.ili934xhax import ILI9341, color565, color565n
from machine import SPI, Pin, I2C
import the_pad.mcpnew as mcpnew

spi = SPI(
    2,
    baudrate=40000000,
    miso=Pin(19),
    mosi=Pin(23),
    sck=Pin(18))
display = ILI9341(spi,
    cs=Pin(0),
    dc=Pin(15),
    rst=Pin(5))

pin_clk = 13
pin_data = 4

clk = Pin(pin_clk, Pin.OUT)
data = Pin(pin_data, Pin.OUT)

clk.value(0)
data.value(0)

I2C_SCL = 27
I2C_SDA = 32

i2c = I2C(scl = Pin(I2C_SCL), sda = Pin(I2C_SDA))

io = mcpnew.MCP23017(i2c, address=0x20) #, gpioScl=I2C_SCL, gpioSda=I2C_SDA) # 32

def write_led(dat):
    for i in range(32):
        data.value(dat & 1)
        clk.value(1)
        clk.value(0)
        dat = dat >> 1

def write_color(r,g,b,gl):
    data.value(1)
    for i in range(3):
        clk.value(1)
        clk.value(0)

    for i in range(5):
        data.value(gl & (1 << (4-i)))
        clk.value(1)
        clk.value(0)

    for c in [r, g, b]:
        for i in range(8):
            data.value(c & (1 << (7-i)))
            clk.value(1)
            clk.value(0)





pipz = [4, 7, 8, 11]

for a in pipz:
    io.setup(a, mcpnew.IN)
    io.pullup(a, True)

display.erase()
display.set_pos(0,0)
display.width = 240
display.height = 320

display.fill_rectangle(0, 0, 240, 320, color565n(0, 0, 0))

display.set_color(color565n(220, 220, 160), color565n(0,0,30))

display.set_pos(50, 50)
display.write("Tetris")

display.set_pos(50, 70)
display.write("Snake")

display.set_pos(50, 90)
display.write("Weather report")

display.set_pos(50, 110)
display.write("3D dungeon")


selection = 0
moveu = False
moved = False

display.fill_rectangle(43, 52 + selection*20, 4, 4, color565n(180, 180, 120))

while True:
    write_led(0)
    for a in range(0, 4):
        if selection == a:
            write_color(33, 120, 100, 10)
        else:
            write_color(0, 0, 0, 0)

    write_led(~0)

    if not io.input(8):
        if not moveu:
            display.fill_rectangle(43, 52 + selection*20, 4, 4, color565n(0, 0, 0))
            selection -= 1
            if selection < 0:
                selection = 3

            display.fill_rectangle(43, 52 + selection*20, 4, 4, color565n(180, 180, 120))
            moveu = True
    else:
        moveu = False

    if not io.input(11):
        if not moved:
            display.fill_rectangle(43, 52 + selection*20, 4, 4, color565n(0, 0, 0))
            selection += 1
            if selection > 3:
                selection = 0

            moved = True
            display.fill_rectangle(43, 52 + selection*20, 4, 4, color565n(180, 180, 120))
    else:
        moved = False

    if not io.input(7):
        break

    if not io.input(4):
        if selection == 0:
            import tetrix
            tetrix.run()

        if selection == 1:
            import snek
            snek.run()

        if selection == 2:
            import temperature
            temperature.run()

        if selection == 3:
            import rtracnew
            rtracnew.run()