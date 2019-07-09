from the_pad.ili934xhax import ILI9341, color565, color565n
from machine import SPI, Pin, I2C
import the_pad.mcpnew as mcpnew
import framebuf
import random

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

pinz = [PIN_LEFT, PIN_RIGHT, PIN_UP, PIN_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_UP, BUTTON_DOWN]

DIR_LEFT = 3
DIR_RIGHT = 4
DIR_UP = 5
DIR_DOWN = 6

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class area(object):
    def __init__(self, disp):
        self.display = disp
        self.tiles = []

        self.asizex = 30
        self.asizey = 30

        self.toppadding = 10

        self.bgcol = color565n(0, 0, 30)
        self.snekcol = color565n(180, 170, 40)
        self.wallcol = color565n(30, 30, 140)
        self.applecol = color565n(180, 40, 40)

        self.tilesize = 240 // self.asizex #16

        self.display.set_pos(0, 0)
        self.display.set_color(color565n(220, 220, 160), color565n(0,0,30))
        self.display.write("score: ")

        self.initializelevel()
        self.spawnnewapple()


    def initializelevel(self):
        self.tiles.clear()

        for b in range(0, self.asizex):
            for a in range(0, self.asizey):
                if a == 0 or a == self.asizex - 1 or b == 0 or b == self.asizey - 1:
                    self.tiles.append(1) #wall
                    self.renderblock(a,b,1)
                else:
                    self.tiles.append(0) #empty space

    def spawnnewapple(self):
        while True:
            nx = random.randint(1, self.asizex - 2)
            ny = random.randint(1, self.asizey - 2)

            if self.getblock(nx, ny) == 0: #only make new apple in empty spot
                self.setanddrawblock(nx, ny, 2)
                break

    def getblock(self, x, y):
        if 0 <= x < self.asizex and 0 <= y < self.asizey:
            return self.tiles[x+y*self.asizex]
        else:
            return 99

    def setblock(self, x, y, bid):
        self.tiles[x+y*self.asizex] = bid

    def setanddrawblock(self, x, y, bid): #same as setblock, but also renders the updated tile
        self.tiles[x+y*self.asizex] = bid
        self.renderblock(x,y,bid)

    def renderblock(self, x, y, bid = -1):
        if bid > -1:
            blockid = bid
        else:
            blockid = self.getblock(x,y)

        tilesize = self.tilesize

        if blockid == 0: #empty tile
            self.display.fill_rectangle(x*tilesize, y*tilesize + self.toppadding, tilesize, tilesize, self.bgcol)
        
        if blockid == 1: #wall
            self.display.fill_rectangle(x*tilesize, y*tilesize + self.toppadding, tilesize, tilesize, self.wallcol)
            
        if blockid == 2: #apple
            self.display.fill_rectangle(x*tilesize, y*tilesize + self.toppadding, tilesize, tilesize, self.bgcol)
            self.display.fill_rectangle(x*tilesize+2, y*tilesize+2 + self.toppadding, tilesize-4, tilesize-4, self.applecol)

        if blockid > 2: #snake
            self.display.fill_rectangle(x*tilesize, y*tilesize + self.toppadding, tilesize, tilesize, self.snekcol)


class snake(object):
    def __init__(self, disp, area):
        self.display = disp
        self.area = area

        self.score = 0

        self.feedcounter = 2

        self.snake = []

        self.dead = False

        self.snakespeed = 10
        self.snakecounter = 0

        self.x = 2
        self.y = 2

        self.direction = DIR_RIGHT
        self.nextdirection = DIR_RIGHT

        self.initsnake()

    def initsnake(self):
        self.snake.append((self.x, self.y, self.direction))

        self.addscore(0)

    def movesnake(self):
        if not self.dead:
            self.snakecounter += 1
            if self.snakecounter > self.snakespeed:
                self.snakecounter = 0
                self.elongatesnake()

                if self.feedcounter > 0:
                    self.feedcounter -= 1
                    self.addscore(1)
                else:
                    self.shrinksnake()

    def addscore(self, score):
        self.score += score
        self.display.set_pos(40, 0)
        self.display.write(str(self.score))

    def eatapple(self):
        self.feedcounter += 5
        self.addscore(10)
        self.area.spawnnewapple()

    def crash(self):
        self.dead = True
        self.display.set_pos(80, 120)
        self.display.set_color(color565n(250, 55, 55), color565n(0,0,0))
        self.display.write("You crashed!!")

    def elongatesnake(self):
        #elongates snake by 1 in the front
        ex = self.x
        ey = self.y

        self.direction = self.nextdirection

        toadd = directions[self.direction-3]

        ex += toadd[0]
        ey += toadd[1]

        #check if crash or apple
        newspace = self.area.getblock(ex, ey)

        print(newspace)

        if newspace == 1 or newspace > 2:
            self.crash()
            return

        if newspace == 2:
            #apple
            self.eatapple()

        #register and render the new snake part
        self.area.setanddrawblock(ex, ey, self.direction)
        self.snake.append((ex, ey, self.direction))

        self.x = ex
        self.y = ey



    def shrinksnake(self):
        #shrinks snake by 1 from the back
        todelete = self.snake[0]

        self.area.setanddrawblock(todelete[0], todelete[1], 0)

        del self.snake[0]

    def changedirection(self, direction):
        olddir = directions[self.direction-3]
        newdir = directions[direction-3]

        if (olddir[0] and newdir[0]) or (olddir[1] and newdir[1]):
            #only changes direction if it makes sense
            pass
        else:
            self.nextdirection = direction


def run():
    io = mcpnew.MCP23017(i2c, address=0x20) # 32

    for a in pinz:
        io.setup(a, mcpnew.IN)
        io.pullup(a, True)

    display.erase()
    display.set_pos(0,0)
    display.width = 240
    display.height = 320

    display.fill_rectangle(0, 0, 240, 320, color565n(0, 0, 30))

    omraad = area(display)

    snek = snake(display, omraad)
    snek.initsnake()

    while True:
        if not io.input(PIN_LEFT):
            snek.changedirection(DIR_LEFT)

        if not io.input(PIN_RIGHT):
            snek.changedirection(DIR_RIGHT)

        if not io.input(PIN_DOWN):
           snek.changedirection(DIR_DOWN)

        if not io.input(PIN_UP):
            snek.changedirection(DIR_UP)

        #if not io.input(BUTTON_UP):
        #    break

        snek.movesnake()

