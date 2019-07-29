# display - official
from the_pad.ili934xnew import ILI9341, color565
from machine import SPI, Pin
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

I2C_SCL = 27
I2C_SDA = 32

i2c = I2C(scl = Pin(I2C_SCL), sda = Pin(I2C_SDA))

BUTTON_LEFT = 5
BUTTON_RIGHT = 6
BUTTON_UP = 7
BUTTON_DOWN = 4

PIN_LEFT = 9
PIN_RIGHT = 10
PIN_UP = 8
PIN_DOWN = 11

DIR_STOPPED = 0
DIR_LEFT = 1
DIR_RIGHT = 2
DIR_UP = 3
DIR_DOWN = 4

dirs = [(0,0), (1, 0), (-1, 0), (0, -1), (0, 1)]

pinz = [PIN_LEFT, PIN_RIGHT, PIN_UP, PIN_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_UP, BUTTON_DOWN]

#pinz = range(0,16)

io = mcpnew.MCP23017(i2c, address=0x20) # 32

class field(object):
    def __init__(self, disp):
        self.omraad = []

        self.height = 24
        self.width = 24

        self.dots = 0

        self.display = disp

        self.blockwidth = 240 // self.width

        self.colors = [color565(0,0,30), color565(50,50,200), color565(0,0,30)]

        for a in range(0, self.height*self.width):
            self.omraad.append(0)

    def getpoint(self, x, y):
        return self.omraad[x+y*self.width]

    def setpoint(self, x, y, pt):
        self.omraad[x+y*self.width] = pt

    def renderblock(self, x, y):
        bappo = self.getpoint(a,b)
        self.display.fill_rectangle(a*blockwidth, b*blockwidth, blockwidth, blockwidth, cols[bappo])

        if bappo == 0:
            self.renderdot(x,y)

    def renderdot(self, x, y):
        self.display.fill_rectangle((x*self.blockwidth)+4, (y*self.blockwidth)+4, self.blockwidth-8, self.blockwidth-8, color565(200, 200, 200))

    def eatdot(self, x, y):
        if self.getpoint(x,y) == 0:
            self.setpoint(x,y, 2)
            self.dots -= 1

    def initfield(self):
        gp = 0
        self.omraad = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
                       1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
                       1,0,1,1,0,1,0,1,0,1,0,1,0,1,1,1,0,1,1,0,1,1,0,1,
                       1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,1,
                       1,0,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,0,1,0,1,
                       1,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1,
                       1,0,1,0,1,1,1,1,1,1,1,0,0,0,1,0,1,1,1,1,0,1,1,1,
                       0,0,1,0,1,2,2,2,2,2,1,1,1,0,1,0,1,0,0,0,0,0,0,0,
                       1,0,0,0,1,2,2,2,2,2,1,0,0,0,1,0,1,0,1,1,1,0,1,1,
                       1,0,1,1,1,2,2,2,2,2,1,0,1,1,1,0,1,0,0,0,1,0,0,1,
                       1,0,0,0,1,2,2,2,2,2,1,0,0,0,0,0,1,1,1,0,1,1,0,1,
                       1,1,1,0,1,1,1,2,1,1,1,1,1,1,1,0,1,1,0,0,0,1,0,1,
                       1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
                       1,0,1,1,0,1,0,1,0,1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,
                       1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
                       1,1,1,1,0,1,0,1,1,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,
                       1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,
                       1,0,1,1,1,1,1,1,0,1,0,1,0,1,1,1,1,1,0,1,0,0,0,1,
                       1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,1,0,1,
                       1,0,1,0,1,1,0,1,0,1,0,1,0,1,1,0,1,1,1,1,0,0,0,1,
                       1,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,
                       1,0,1,1,1,1,0,1,0,1,0,1,0,1,1,1,0,1,0,1,0,1,0,1,
                       1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
                       1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

    def render(self):
        blockwidth = self.blockwidth
        cols = self.colors
        self.dots = 0

        for a in range(0, self.width):
            for b in range(0, self.height):
                bappo = self.getpoint(a,b)
                self.display.fill_rectangle(a*blockwidth, b*blockwidth, blockwidth, blockwidth, cols[bappo])

                if bappo == 0:
                    #self.display.fill_rectangle((a*blockwidth)+4, (b*blockwidth)+4, blockwidth-8, blockwidth-8, color565(200, 200, 200))
                    self.renderdot(a,b)
                    self.dots += 1


class player(object):
    def __init__(self, disp, fild, scale):
        self.field = fild
        self.display = disp

        self.scale = scale

        self.ex = 22
        self.ey = 22

        self.progress = 0

        self.speed = 2

        self.dudecol = color565(250, 250, 0)

        self.direction = DIR_STOPPED
        self.nextdir = DIR_STOPPED

        self.score = 0

        self.bgcol = color565(0,0,30)


    def renderscore(self):
        # dette går altfor tregt - og texten blir speilvendt...
        '''display.set_pos(0, 260)
        display.set_color(self.dudecol, color565(0,0,0))
        display.write("horse ist gut: "+str(self.score)+"   ")'''

    def renderblank(self):
        if self.direction == DIR_LEFT:
            self.display.fill_rectangle(self.getxpos(), self.getypos()+1, 2, self.scale-2, self.bgcol)
        if self.direction == DIR_RIGHT:
            self.display.fill_rectangle(self.getxpos()+self.scale-2, self.getypos()+1, 2, self.scale-2, self.bgcol)
        if self.direction == DIR_UP:
            self.display.fill_rectangle(self.getxpos()+1, self.getypos()+self.scale-2, self.scale-2, 2, self.bgcol)
        if self.direction == DIR_DOWN:
            self.display.fill_rectangle(self.getxpos()+1, self.getypos(), self.scale-2, 2, self.bgcol)


    def move(self):

        self.renderblank()

        self.progress+=self.speed



        if self.progress > self.scale or self.direction == DIR_STOPPED:
            self.progress = 0

            hex = self.ex
            hey = self.ey

            if self.direction == DIR_LEFT:
                self.ex += 1
            if self.direction == DIR_RIGHT:
                self.ex -= 1
            if self.direction == DIR_UP:
                self.ey -= 1
            if self.direction == DIR_DOWN:
                self.ey += 1

            if self.ex != hex or self.ey != hey:
                self.field.eatdot(self.ex, self.ey)

            self.direction = self.nextdir

            tx = dirs[self.direction][0]
            ty = dirs[self.direction][1]

            if self.field.getpoint(self.ex+tx, self.ey+ty) == 1:
                self.direction = DIR_STOPPED
                self.nextdir = DIR_STOPPED

    def getxpos(self):
        ex = self.ex * self.scale

        if self.direction == DIR_LEFT:
            ex += self.progress

        if self.direction == DIR_RIGHT:
            ex -= self.progress

        return ex

    def getypos(self):
        ey = self.ey * self.scale

        if self.direction == DIR_UP:
            ey -= self.progress

        if self.direction == DIR_DOWN:
            ey += self.progress

        return ey


    def render(self):
        self.display.fill_rectangle(self.getxpos()+1, self.getypos()+1, self.scale-2, self.scale-2, self.dudecol)

    def changedir(self, newdir):
        self.nextdir = newdir


def run():

    for a in pinz:
        io.setup(a, mcpnew.IN)
        io.pullup(a, True)

    omraad = field(display)

    omraad.initfield()

    display.erase()
    display.set_pos(0,0)
    display.width = 240
    display.height = 320

    display.fill_rectangle(0, 0, 239, 319, color565(0,0,30))

    ex = 22
    ey = 22

    mx = 0
    my = 0

    bgcol = color565(0,0,30)


    wid = omraad.blockwidth

    plr = player(display, omraad, wid)

    omraad.render()

    while True:

        if not io.input(PIN_LEFT):
            plr.changedir(DIR_LEFT)

        if not io.input(PIN_RIGHT):
            plr.changedir(DIR_RIGHT)

        if not io.input(PIN_UP):
            plr.changedir(DIR_UP)

        if not io.input(PIN_DOWN):
            plr.changedir(DIR_DOWN)

        plr.move()

        plr.render()

        plr.renderscore()

        if omraad.dots == 0:
            break


        if not io.input(BUTTON_UP):
            break
