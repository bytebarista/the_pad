from the_pad.ili934xhax import ILI9341, color565, color565n
from machine import SPI, Pin, I2C
import the_pad.mcpnew as mcpnew
import framebuf
import random
import the_pad.bme280_int as bme280_int

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

I2C_SCL = 27
I2C_SDA = 32

i2c = I2C(scl = Pin(I2C_SCL), sda = Pin(I2C_SDA))

BUTTON_LEFT = 5
BUTTON_RIGHT = 6
BUTTON_UP = 7
BUTTON_DOWN = 4

PIN_LEFT = 9 #gucci
PIN_RIGHT = 10 #gucci
PIN_UP = 8 #gucci
PIN_DOWN = 11 #gucci

pinz = [PIN_LEFT, PIN_RIGHT, PIN_UP, PIN_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_UP, BUTTON_DOWN]

io = mcpnew.MCP23017(i2c, address=0x20)#, gpioScl=I2C_SCL, gpioSda=I2C_SDA) # 32


def run():
    for a in pinz:
        io.setup(a, mcpnew.IN)
        io.pullup(a, True)

    bme = bme280_int.BME280(i2c = i2c)

    display.erase()
    display.set_pos(0,0)
    display.width = 240
    display.height = 320

    display.fill_rectangle(0, 0, 240, 320, color565n(0, 0, 70))

    tmax = -100.0
    tmin = 100.0

    display.set_color(color565n(220, 220, 220), color565n(0,0,70))

    display.set_pos(120, 85)
    display.write("Pressure")

    display.set_pos(120, 158)
    display.write("Humidity")

    hmax = 0
    hmin = 100

    for a in range(0, 9):
        display.fill_rectangle(45, 30 + (a * 30), 5, 1, color565n(220, 220, 220))
        display.set_pos(50, 30 + (a * 30))
        pelp = ((9-a)-3)*10
        display.write(str(pelp))

    while True:

        bmevals = bme.read_compensated_data()

        temp = bmevals[0]/100

        press = bmevals[1]//256
        atm = press / 101325
        hg = press / 133.322
        ihg = press / 3386.389

        humid = bmevals[2] / 1024

        sizep = 240 - (int(temp) + 20) * 3
        grisep = 240 - sizep

        tmaxp = 240 - (int(tmax) + 20) * 3
        tminp = 240 - (int(tmin) + 20) * 3

        if sizep < tmaxp:
            display.fill_rectangle(20, tmaxp+30, 5, 1, color565n(0, 0, 70))
            tmax = temp
            display.fill_rectangle(20, 240 - (int(tmin) + 20) * 3 + 30, 5, 1, color565n(20, 130, 180))
            display.fill_rectangle(20, 240 - (int(tmax) + 20) * 3 + 30, 5, 1, color565n(180, 130, 20))

        if sizep > tminp:
            display.fill_rectangle(20, tminp + 30, 5, 1, color565n(0, 0, 70))
            tmin = temp
            display.fill_rectangle(20, 240 - (int(tmax) + 20) * 3 + 30, 5, 1, color565n(180, 130, 20))
            display.fill_rectangle(20, 240 - (int(tmin) + 20) * 3 + 30, 5, 1, color565n(20, 130, 180))

        display.set_pos(20, 287)
        #display.set_color(color565n(220, 220, 220), color565n(0,0,0))
        display.write(str(temp))

        display.set_pos(120, 97)
        display.write(str(round(atm,3)) + " atm   ")
        display.set_pos(120, 107)
        display.write(str(round(press,0)) + " Pa   ")
        display.set_pos(120, 117)
        display.write(str(round(hg,1)) + " mm Hg   ")
        display.set_pos(120, 127)
        display.write(str(round(ihg,2)) + " in Hg   ")

        display.set_pos(120, 170)
        display.write(str(round(humid,2)) + " %")

        if humid > hmax:
            hmax = humid
            display.set_pos(120, 195)
            display.write("max: " + str(round(hmax,2)) + " %")

        if humid < hmin:
            hmin = humid
            display.set_pos(120, 205)
            display.write("min: " + str(round(hmin,2)) + " %")

        display.fill_rectangle(30, 30, 15, sizep-1, color565n(0,0,0))
        display.fill_rectangle(30, sizep+30, 15, grisep, color565n(140,180,140))


        if not io.input(BUTTON_UP):
            break