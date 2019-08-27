from the_pad.ili934xhax import ILI9341, color565, color565n
from machine import SPI, Pin, I2C
import the_pad.mcpnew as mcpnew

import framebuf
import random

spi = SPI(2, baudrate=40000000, miso=Pin(19), mosi=Pin(23), sck=Pin(18))
display = ILI9341(spi, cs=Pin(0), dc=Pin(15), rst=Pin(5))

i2c = I2C(scl=Pin(27), sda=Pin(32))

BUTTON_LEFT = 5
BUTTON_RIGHT = 6
BUTTON_UP = 7
BUTTON_DOWN = 4

PIN_LEFT = 9
PIN_RIGHT = 10
PIN_UP = 8
PIN_DOWN = 11

pinz = [PIN_LEFT, PIN_RIGHT, PIN_UP, PIN_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_UP, BUTTON_DOWN]


class tilemanager(object):
    def __init__(self, disp):
        self.display = disp

        self.blocksize = 16 #pixel height and width for blocks

        self.scrolled = 0 #how many rows have passed

        self.miniscrolled = -1 #how many pixels within row self.scrolled have passed

        self.levelheight = 255

        self.numblockshoriz = 240 // self.blocksize #screen 15 blocks wide
        self.numblocksvert = 320 // self.blocksize  #screen 20 blocks tall

        self.brickbuf = bytearray(self.blocksize * self.blocksize * 2)
        self.backbuf = bytearray(self.blocksize * self.blocksize * 2)
        self.blockbuf = bytearray(self.blocksize * self.blocksize * 2)
        self.coinbuf = bytearray(self.blocksize * self.blocksize * 2)

        self.tiles = [
            framebuf.FrameBuffer(self.backbuf, self.blocksize, self.blocksize, framebuf.RGB565),
            framebuf.FrameBuffer(self.brickbuf, self.blocksize, self.blocksize, framebuf.RGB565),
            framebuf.FrameBuffer(self.blockbuf, self.blocksize, self.blocksize, framebuf.RGB565),
            framebuf.FrameBuffer(self.coinbuf, self.blocksize, self.blocksize, framebuf.RGB565)
        ]

        # data for tile placement (level self.levelheight tiles height)
        self.level = bytearray(self.numblockshoriz * self.levelheight)

        #setup tiles

        #simple blank (background) tile
        self.tiles[0].fill(color565(66, 66, 200))

        #brick tile
        self.tiles[1].fill(color565(123, 80, 20))
        self.tiles[1].hline(0, 3, 16, color565(0, 0, 0))
        self.tiles[1].hline(0, 7, 16, color565(0, 0, 0))
        self.tiles[1].hline(0, 11, 16, color565(0, 0, 0))
        self.tiles[1].hline(0, 15, 16, color565(0, 0, 0))

        self.tiles[1].vline(8, 0, 4, color565(0, 0, 0))
        self.tiles[1].vline(15, 0, 4, color565(0, 0, 0))
        self.tiles[1].vline(8, 8, 4, color565(0, 0, 0))
        self.tiles[1].vline(15, 8, 4, color565(0, 0, 0))

        self.tiles[1].vline(4, 4, 4, color565(0, 0, 0))
        self.tiles[1].vline(12, 4, 4, color565(0, 0, 0))
        self.tiles[1].vline(4, 12, 4, color565(0, 0, 0))
        self.tiles[1].vline(12, 12, 4, color565(0, 0, 0))

        #steel tile
        self.tiles[2].fill(color565(99, 99, 99))
        self.tiles[2].vline(0, 0, 16, color565(0, 0, 0))
        self.tiles[2].vline(15, 0, 16, color565(0, 0, 0))
        self.tiles[2].hline(0, 0, 16, color565(0, 0, 0))
        self.tiles[2].hline(0, 15, 16, color565(0, 0, 0))

        self.tiles[2].pixel(2, 2, color565(0, 0, 0))
        self.tiles[2].pixel(13, 2, color565(0, 0, 0))
        self.tiles[2].pixel(2, 13, color565(0, 0, 0))
        self.tiles[2].pixel(13, 13, color565(0, 0, 0))

        # coin tile
        self.tiles[3].fill(color565(66, 66, 200))
        self.tiles[3].hline(6, 2, 4, color565(230, 156, 33))
        self.tiles[3].hline(10, 2, 2, color565(0, 0, 0))

        self.tiles[3].fill_rect(5, 3, 6, 12, color565(230, 156, 33))
        self.tiles[3].fill_rect(11, 3, 2, 2, color565(0, 0, 0))

        self.tiles[3].vline(4, 5, 8, color565(230, 156, 33))
        self.tiles[3].vline(11, 5, 8, color565(230, 156, 33))
        self.tiles[3].vline(12, 5, 8, color565(0, 0, 0))
        self.tiles[3].vline(13, 5, 8, color565(0, 0, 0))

        self.tiles[3].fill_rect(11, 13, 2, 2, color565(0, 0, 0))

        self.tiles[3].hline(6, 15, 4, color565(230, 156, 33))
        self.tiles[3].hline(10, 15, 2, color565(0, 0, 0))

        self.tiles[3].vline(6, 5, 8, color565(156, 74, 0))
        self.tiles[3].hline(7, 4, 2, color565(156, 74, 0))
        self.tiles[3].vline(9, 5, 8, color565(0, 0, 0))
        self.tiles[3].hline(7, 13, 2, color565(0, 0, 0))

        self.rowbuf = bytearray(self.numblockshoriz * self.blocksize * self.blocksize * 2) #one row of tiles
        self.frowbuf = framebuf.FrameBuffer(self.rowbuf, self.blocksize * self.numblockshoriz, self.blocksize, framebuf.RGB565)
        self.rowbufmv = memoryview(self.rowbuf)

    def generatelevel(self): #just decides which blocks are placed where
        for y in range(0, self.levelheight):
            for x in range(0, self.numblockshoriz):
                block_id = random.randint(0, 12)

                if block_id > 3:
                    block_id = 0

                if y < 2:
                    block_id = 1

                #bytebarista logo
                if 72 > y > 50:
                    block_id = 0

                    if 2 < x < 12 and 64 < y < 71:
                        block_id = 2

                    if 1 < x < 13 and 67 < y < 70:
                        block_id = 2

                    if 2 < x < 12 and 59 < y < 65:
                        block_id = 1

                    if 3 < x < 11 and 57 < y < 60:
                        block_id = 1

                    if 3 < x < 11 and 53 < y < 58:
                        block_id = 2

                self.setblock(x, y, block_id)

        #B in ByteBarista logo
        self.setblock(6, 63, 0)
        self.setblock(6, 62, 0)
        self.setblock(6, 61, 0)
        self.setblock(6, 60, 0)
        self.setblock(6, 59, 0)

        self.setblock(7, 63, 0)
        self.setblock(7, 61, 0)
        self.setblock(7, 59, 0)

        self.setblock(8, 62, 0)
        self.setblock(8, 60, 0)

    def setblock(self, x, y, block_id):
        self.level[y * self.numblockshoriz + x] = block_id

    def filldrawbuf(self, rownum): #row 0 is bottom
        #fills row draw buffer with tiles from row rownum
        transparent = color565n(255, 0, 255)
        bsize = self.blocksize
        numblockshoriz = self.numblockshoriz
        for x in range(0, numblockshoriz):
            tileid = self.level[rownum * numblockshoriz + x]
            self.frowbuf.blit(self.tiles[tileid], x*bsize, 0, transparent)

    def drawdrawbuf(self, rownum): #row 0 is bottom
        #draws the row draw buffer at position y
        self.display._writeblock(0, 320 - ((rownum+1) * self.blocksize), 240, 320 - ((rownum) * self.blocksize), self.rowbuf)

    def renderlevel(self): #renders whole level, used at start
        for y in range(self.scrolled, self.scrolled + self.numblocksvert):
            self.filldrawbuf(y)
            self.drawdrawbuf(y)

        self.filldrawbuf(self.numblocksvert+1) #next line to show

    def scroll(self, scrolldist):
        self.miniscrolled += scrolldist

        if self.miniscrolled >= self.blocksize: #warning! scroll larger than blocksize = bug
            self.miniscrolled -= self.blocksize
            self.scrolled += 1

            maxscroll = self.levelheight - self.numblocksvert - 2

            if self.scrolled > maxscroll:
                self.scrolled = maxscroll

            self.filldrawbuf(self.scrolled + self.numblocksvert + 1)


        scrollert = ((self.scrolled * self.blocksize)+self.miniscrolled)

        yy = 319 - (scrollert % 320)

        sm = ((15-self.miniscrolled) * 480)
        sl = ((15-self.miniscrolled) * 480) + (480)

        self.display._writeblock(0, yy, 240, yy, self.rowbufmv[sm:sl])#draws one pixel row from rowbuf

        self.display.scroll(-scrolldist)


def run():
    io = mcpnew.MCP23017(i2c, address=0x20)  # 32

    for a in pinz:
        io.setup(a, mcpnew.IN)
        io.pullup(a, True)

    display.erase()
    display.set_pos(0, 0)
    display.width = 240
    display.height = 320

    display.fill_rectangle(0, 0, 240, 320, color565n(0, 0, 30))

    tilemngr = tilemanager(display)

    tilemngr.generatelevel()

    tilemngr.renderlevel()

    while io.input(BUTTON_UP):
        if not io.input(PIN_UP):
            tilemngr.scroll(1)

        if not io.input(BUTTON_DOWN):
            display._write(0x21) #inverts display colors

        if not io.input(BUTTON_LEFT):
            display._write(0x20) #normal display colors
