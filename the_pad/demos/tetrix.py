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

io = mcpnew.MCP23017(i2c, address=0x20)

class area(object):
    def __init__(self, disp):
        self.display = disp

        self.blocksize = 14

        self.asizex = 10
        self.asizey = 20

        self.gg = False

        self.ablocksflipped = 0

        self.linesremoved = 0

        self.score = 0

        self.blocks = []

        self.ablocks = []
        self.ablocksid = 1
        self.nextblocksid = 3
        self.ablocksx = 0
        self.ablocksy = 0


        self.blockshapes =[
            [(0,1),(1,1),(1,0),(2,0)],
            [(0,0),(1,1),(1,0),(2,1)],
            [(0,0),(0,1),(0,2),(1,2)],
            [(1,0),(1,1),(1,2),(0,2)],
            [(0,0),(0,1),(1,0),(1,1)],
            [(1,0),(1,1),(0,1),(2,1)],
            [(1,0),(1,1),(1,2),(1,3)]
        ]

        self.speed = 40
        self.counter = 0

        self.level = 1
        self.levelcounter = 0

        self.display.set_pos(self.asizex*self.blocksize+20, 20)
        self.display.set_color(color565n(220, 220, 220), color565n(0,0,0))
        self.display.write("next")


        self.display.set_pos(self.asizex*self.blocksize+20, 120)
        self.display.write("score")

        self.display.set_pos(self.asizex*self.blocksize+20, 150)
        self.display.write("lines")

        self.display.set_pos(self.asizex*self.blocksize+20, 180)
        self.display.write("level")

        self.renderlevel()
        self.renderscore()

        self.buffer = bytearray(self.blocksize * self.asizex * self.blocksize * 5 * 2) # hele bredden, max block size 4x4 + 1 buffer over

        self.ablockbuf = framebuf.FrameBuffer(self.buffer, self.blocksize * self.asizex, self.blocksize * 5, framebuf.RGB565)

        self.nextbuffer = bytearray(self.blocksize * 4 * self.blocksize * 4 * 2)
        self.nextblockbuf = framebuf.FrameBuffer(self.nextbuffer, self.blocksize * 4, self.blocksize * 4, framebuf.RGB565)

        self.colors = [color565(0,0,0), color565(200,0,0), color565(0,200,0), color565(0,0,200), color565(150, 150, 0),
                       color565(150, 150, 150), color565(150, 0, 150), color565(200, 150, 50), color565(50, 250, 150), color565(50, 50, 50)]

    def start(self):
        self.setupboard()
        self.spawnnewablocks()

    def update(self):
        if not self.gg:
            self.counter += 1
            if self.counter > self.speed:
                self.moveablocks(0,1)
                self.counter = 0

    def boost(self):
        self.counter += 10

    def nextlevel(self):
        self.level += 1
        self.levelcounter -= 10

        self.speed -= 2
        if self.speed < 5:
            self.speed = 5

        self.renderlevel()

    def renderlevel(self):
        self.display.set_pos(self.asizex*self.blocksize+30, 170)
        self.display.write(str(self.level))

    def renderscore(self):
        self.display.set_pos(self.asizex*self.blocksize+30, 110)
        #self.display.set_color(color565n(220, 220, 220), color565n(0,0,0))
        self.display.write(str(self.score))
        self.display.set_pos(self.asizex*self.blocksize+30, 140)
        self.display.write(str(self.linesremoved))

    def addscore(self, lines):
        self.score += lines*lines
        self.linesremoved += lines
        self.levelcounter += lines

        if self.levelcounter > 9:
            self.nextlevel()

        self.renderscore()

    def moveablocks(self, x, y):
        if y == 1:
            landed = False
            for a in self.ablocks:
                if self.getblock(a[0]+self.ablocksx, a[1]+self.ablocksy+1) > 0:
                    landed = True

            if landed:
                self.landablocks()
            else:
                self.actuallymoveablocks(0,1)

        if x != 0:
            collide = False
            for a in self.ablocks:
                if self.getblock(a[0]+x+self.ablocksx, a[1]+self.ablocksy) > 0:
                    collide = True

            if not collide:
                self.actuallymoveablocks(x,0)

    def actuallymoveablocks(self,x,y):
        self.ablocksx += x
        self.ablocksy += y

        self.updateblockbuf()
        self.renderblockbuf()

    def renderblockbuf(self):
        wid = self.blocksize

        y = ((self.ablocksy+4)*wid)-1

        '''
        if y > 306:
            y = 306
        '''

        #display.blit(self.ablockbuf, self.ablocksx*wid, self.ablocksy*wid, wid*4, wid*4)
        self.display._writeblock(2, ((self.ablocksy-1)*wid), self.asizex*wid + 1, y, self.buffer)

    def rendernextblock(self):
        wid = self.blocksize

        self.nextblockbuf.fill_rect(0, 0,4*wid,4*wid,self.colors[0])

        pep = self.nextblocksid

        for a in self.blockshapes[pep-1]:
            self.nextblockbuf.fill_rect(a[0]*wid, a[1]*wid,wid,wid,self.colors[pep])

        self.display._writeblock(self.asizex*self.blocksize+20, 30, self.asizex*self.blocksize+20+wid*4-1, 30+wid*4-1, self.nextblockbuf)

    def updateblockbuf(self):

        wid = self.blocksize
        ex = self.ablocksx
        ey = self.ablocksy

        for a in range(0,self.asizex):
            for b in range(0,5):
                pep = self.getblock(a, ey+b-1)
                if pep == 99:
                    pep = 0

                self.ablockbuf.fill_rect(a*wid, ((b)*wid),wid,wid,self.colors[pep])

        if ey+3 == self.asizey:
            self.ablockbuf.hline(0, 4*wid+1, wid*self.asizex, color565(200, 200, 200))
            self.ablockbuf.hline(0, 4*wid+2, wid*self.asizex, color565(200, 200, 200))

        if ey+2 == self.asizey:
            self.ablockbuf.hline(0, 3*wid+1, wid*self.asizex, color565(200, 200, 200))
            self.ablockbuf.hline(0, 3*wid+2, wid*self.asizex, color565(200, 200, 200))

        for a in self.ablocks:
            self.ablockbuf.fill_rect((ex+a[0])*wid, (a[1]+1)*wid, wid, wid, self.colors[self.ablocksid])

    def rotateblock(self, direction):
        original = self.ablocksflipped

        self.ablocksflipped += direction
        if self.ablocksflipped < 0:
            if self.ablocksid == 7 or self.ablocksid == 1 or self.ablocksid == 2:
                self.ablocksflipped = 1
            else:
                self.ablocksflipped = 3

        if self.ablocksflipped > 3 or (self.ablocksflipped > 1 and (self.ablocksid == 7 or self.ablocksid == 1 or self.ablocksid == 2)): #egen regel for staven og zigzags
            self.ablocksflipped = 0

        if self.ablocksid == 5: #kube kan ikke rotere
            self.ablocksflipped = 0

        self.fillablocks()

        redo = False

        for a in self.ablocks:
            if self.getblock(a[0]+self.ablocksx, a[1]+self.ablocksy) != 0:
                redo = True
                break

        if redo:
            self.ablocksflipped = original
            self.fillablocks()

        self.updateblockbuf()
        self.renderblockbuf()

    def fillablocks(self):
        self.ablocks = []

        for a in self.blockshapes[self.ablocksid-1]:

            apo = a[0]-1
            bpo = a[1]-1

            if self.ablocksid == 7:
                if self.ablocksflipped == 1:
                    grab = (bpo, apo)
                else:
                    grab = (apo, bpo)
            else:

                if self.ablocksflipped == 1:
                    grab = (-bpo, apo)
                elif self.ablocksflipped == 2:
                    grab = (-apo, -bpo)
                elif self.ablocksflipped == 3:
                    grab = (bpo, -apo)
                else:
                    grab = (apo, bpo)


            self.ablocks.append((grab[0]+1, grab[1]+1))

    def gameover(self):
        self.gg = True
        self.display.set_pos(((self.asizex*self.blocksize) // 2)-25, 90)
        self.display.set_color(color565n(220, 220, 160), color565n(0,0,0))
        self.display.write("game over")


    def spawnnewablocks(self):
        self.ablocksx = 4
        self.ablocksy = 0

        self.ablocksflipped = 0

        self.ablocksid = self.nextblocksid

        self.nextblocksid = random.randint(1, 7)

        self.rendernextblock()

        self.fillablocks()

        for a in self.ablocks:
            if self.getblock(a[0]+self.ablocksx, a[1]+self.ablocksy) > 0:
                self.gameover()


    def checkforlines(self):
        checklines = []
        for a in self.ablocks:
            gap = a[1]+self.ablocksy
            if gap not in checklines:
                checklines.append(gap)

        eraselines = []
        for a in checklines:
            bopo = True
            for b in range(0, self.asizex):
                if not (0 < self.getblock(b,a) < 8):
                    bopo = False

            if bopo:
                eraselines.append(a)

        if eraselines:

            self.addscore(len(eraselines))

            linesremoved = 0
            for a in range(0, self.asizey):
                y = self.asizey - a
                if linesremoved:
                    for xx in range(0, self.asizex):
                        self.setblock(xx, y+linesremoved, self.getblock(xx, y))

                if y in eraselines:
                    linesremoved += 1

            self.redrawboard()

    def redrawboard(self):
        # use das framebuf
        wid = self.blocksize

        bomraad = 0
        counter = 0

        for a in range(0, self.asizey):
            for b in range(0, self.asizex):
                pep = self.getblock(b,a)
                self.ablockbuf.fill_rect(b*wid, ((a)*wid)-(bomraad*5*wid),wid,wid,self.colors[pep])

            counter += 1
            if counter == 5:
                display._writeblock(2, (bomraad*5)*wid, self.asizex*wid + 1, ((bomraad*5)+5)*wid, self.buffer)

                counter = 0
                bomraad += 1

        self.updateblockbuf()



    def landablocks(self):
        for a in self.ablocks:
            self.setblock(a[0]+self.ablocksx, a[1]+self.ablocksy, self.ablocksid)

        self.checkforlines()

        self.ablocks = []

        self.spawnnewablocks()

    def getblock(self, x, y):
        if 0 <= x < self.asizex and 0 <= y < self.asizey:
            return self.blocks[x+y*self.asizex]
        else:
            return 99

    def rendernewblock(self, x, y, id):
        self.display.fill_rectangle(x*self.blocksize+2, y*self.blocksize+2, self.blocksize, self.blocksize, self.colors[id])

    def renderblock(self, x, y):
        self.display.fill_rectangle(x*self.blocksize+2, y*self.blocksize+2, self.blocksize, self.blocksize, self.colors[self.getblock(x,y)])

    def setblock(self, x, y, pt):
        self.blocks[x+y*self.asizex] = pt

    def setupboard(self):
        self.blocks = []

        for a in range(0, self.asizex*self.asizey+1):
            self.blocks.append(0)

    def renderui(self):
        self.display.fill_rectangle(0, 0, self.blocksize*self.asizex+4, self.blocksize*self.asizey+4, color565n(200, 200, 200))
        self.display.fill_rectangle(2, 2, self.blocksize*self.asizex, self.blocksize*self.asizey, color565n(0, 0, 0))



def run():
    for a in pinz:
        io.setup(a, mcpnew.IN)
        io.pullup(a, True)

    display.erase()
    display.set_pos(0,0)
    display.width = 240
    display.height = 320

    display.fill_rectangle(0, 0, 240, 320, color565(0, 0, 0))

    omraad = area(display)

    #omraad.setupboard()

    omraad.renderui()

    omraad.start()

    rot = False

    movespeed = 20
    movelcounter = 0
    movercounter = 0

    while not omraad.gg:
        omraad.update()

        if not io.input(PIN_LEFT):
            movelcounter += 1
            if movelcounter > movespeed:
                omraad.moveablocks(-1,0)
                movelcounter = 0
        else:
            movelcounter = movespeed

        if not io.input(PIN_RIGHT):
            movercounter += 1
            if movercounter > movespeed:
                omraad.moveablocks(1,0)
                movercounter = 0
        else:
            movercounter = movespeed

        if not io.input(PIN_DOWN):
            omraad.boost()

        if not io.input(BUTTON_LEFT):
            if rot == False:
                omraad.rotateblock(-1)
                rot = True

        if not io.input(BUTTON_RIGHT):
            if rot == False:
                omraad.rotateblock(1)
                rot = True

        if io.input(BUTTON_LEFT) and io.input(BUTTON_RIGHT):
            rot = False


        if not io.input(BUTTON_UP):
            break