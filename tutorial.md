
# To get started look at the Getting Started links in our [wiki](https://github.com/bytebarista/iot_workshop/wiki):


### When setup and connected to your device
Open your serial terminal and run all the code cells in this notebook there to make it run on the device.

#### To copy-paste multiple lines of text to the terminal in one go:
You first have to enter "bulk paste mode", **ctrl + e**, and from there the method for pasting depends on how you set up the connection.

Regardless, when you are done with bulk pasting; finish with **ctrl + d** which will exit and execute the code snippets.

#### IMPORTANT: While not in bulk-paste mode **ctrl + d** soft reboots the device!

#### IMPORTANT_final_V.02: If any of the cells relying on simply importing src code from our repository can't import the module it probably needs to be copied over to the controller via ampy. This also goes for potential work done in the "open tasks" at the end.


# General-purpose Input/Output ([GPIO](https://en.wikipedia.org/wiki/General-purpose_input/output))

### Switching pin output on/off

Turn your controller over and on the back you'll find the microcontroller.

On it there's a tiny green LED. It should be on. Let's turn it off.

The green LED is connected to pin 19 on the microcontroller. By using the [Pin](https://docs.micropython.org/en/latest/esp32/quickref.html#pins-and-gpio) class we can easily change the output of this Pin from on to off:

```python
from machine import Pin

pin_onboard_led = 19
p = Pin(pin_onboard_led, Pin.OUT)
p.off()
```

If you wan't to turn it back on just write **p.on()** in the interactive session

### Dimming the LED

Instead of having the Pin be either on or off all the time, we can instead use Pulse Width Modulation ([PWM](https://docs.micropython.org/en/latest/esp32/quickref.html#pwm-pulse-width-modulation)) to rapidly turn the Pin on and off continuously. PWM is commonly used to adjust the intensity of LEDs.

Let's setup PWM for the LED pin, and specify the settings to dim that LED:

```python
from machine import Pin, PWM

pwm0 = PWM(Pin(19))       
pwm0.freq(100)     
pwm0.duty(20)
```

##### Try, for example, changing the frequency to 5
You can also try setting the frequency up again, but the duty down to 5.

PWM is a technique used to emulate an analog signal, as such:
![image.png](https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Delta_PWM.svg/1920px-Delta_PWM.svg.png)
https://en.wikipedia.org/wiki/Pulse-width_modulation

Reset the LED light by running: **pwm0.deinit()**

### Turn your controller back over again!

Let's try some addressable RGB-LEDs by running a [show](https://github.com/bytebarista/iot_workshop/blob/master/src/led_show.py)!

There are four LEDs on the right side of the display, running vertically up from the *LEDS* tag on the controller.

The cell below runs for a long time, interrupt it as usual by a quick **ctrl + c** in the interactive session. You'll notice how they get "stuck in place" as there is no shutdown signal attached to the *KeyboardInterruptException*.


```python
import led_show

led_show.run()
```

If you are curious about the inner workings on these LEDs you can find the datasheet [here](https://cdn-shop.adafruit.com/datasheets/APA102.pdf) and the singal source code [here](https://github.com/bytebarista/iot_workshop/blob/master/src/led_lights.py)

# Component communication protocols

For communication between components there are two major protocols worth mentioning: [SPI](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface) and [I2C](https://en.wikipedia.org/wiki/I%C2%B2C)

The following controller components are communicating over SPI:
* The main [display](https://cdn-shop.adafruit.com/datasheets/ILI9341.pdf)
* The microSD card reader

The following components are communicating over I2C:
* [GPIO-extender](https://www.microchip.com/wwwproducts/en/MCP23017)
* [BME280](https://www.bosch-sensortec.com/bst/products/all_products/bme280) environmental sensor (temperature, humidity, pressure)
* [MPU9250](https://www.invensense.com/products/motion-tracking/9-axis/mpu-9250/) 9-axis motion sensor
* [display touch driver](https://www.crystalfontz.com/controllers/FocalTech/FT6336G/)


# Serial Peripheral Interface ([SPI](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface))

Let's instantiate an SPI object

[argument explanation](https://docs.micropython.org/en/latest/esp32/quickref.html#hardware-spi-bus)


```python
from machine import Pin, SPI

spi = SPI(2, 40000000, miso=Pin(19), mosi=Pin(23), sck=Pin(18))
```

### MicroSD reader

Given that you have a microSD card on the controller.

You can first mount it:


```python
import os
from sdcard import SDCard

sd = SDCard(spi, cs=Pin(14))

os.mount(sd, '/sd')
```

And confirm that it was mounted:

(you should find a folder called 'sd' in the output)


```python
os.listdir('/')
```

Let's create and write to a file on the SD card and read back from it:


```python
with open('/sd/test.txt', 'w') as f:
    f.write("Hello World!")

with open('/sd/test.txt', 'r') as f:
    print(f.read())
```

### The Display ([driver modified for our display](https://github.com/bytebarista/the_pad/blob/master/the_pad/demos/ili934xhax.py))

Note that the ili934xhax.py also requires glcdfont.py.

Simple example, draws some boxes and writes some text:

```python
from ili934xhax import ILI9341, color565n, color565
from machine import SPI, Pin

display = ILI9341(spi,
    cs=Pin(0),
    dc=Pin(15),
    rst=Pin(5))
display.erase()
display.set_pos(0,0)
display.width = 240
display.height = 320

display.fill_rectangle(0, 0, 50, 50, color565n(180,114,52))
display.fill_rectangle(30, 160, 50, 50, color565n(80,184,152))
display.fill_rectangle(120, 120, 50, 50, color565n(45,114,252))

display.set_pos(50, 50)
display.set_color(color565n(250, 250, 250), color565n(0,0,0))
display.write("Hello")
```


A more interesting example:

```python
import time, random

width = 240
height = 320

screen_x_mid = int(width/2)
screen_y_mid = int(height/2)

UL_square = [0,0, screen_x_mid,screen_y_mid]
UR_square = [screen_x_mid,0, width,screen_y_mid]
LR_square = [screen_x_mid,screen_y_mid, width,height]
LL_square = [0,screen_y_mid, screen_x_mid,height]

squares = [UL_square, UR_square, LR_square, LL_square]

while True:
    try:
        r, g, b = random.randint(40, 225), random.randint(40, 225), random.randint(40, 225)
        fillcolor = color565(r, g, b)
        x, y, x1, y1 = squares[random.randint(0, 3)]
        display.fill_rectangle(x, y, x1, y1, fillcolor)
        time.sleep(0.12)
    except KeyboardInterrupt:
        for s in squares:
            x, y, x1, y1 = s
            display.fill_rectangle(x, y, x1, y1, color565n(40,40,40))
        display.fill_rectangle(0, 0, width, height, color565n(30,30,40))
        display.fill_rectangle(0, 0, width, height, color565n(20,30,20))
        display.fill_rectangle(0, 0, width, height, color565n(20,10,10))
        display.fill_rectangle(0, 0, width, height, color565n(0,0,0))
        break
        
```

# Inter-Integrated Circuit ([I2C](https://en.wikipedia.org/wiki/I²C))

Instantiating an I2C bus is also easy

```python
from machine import Pin, I2C
i2c = I2C(scl = Pin(27), sda = Pin(32))
```

[More detailed information](https://docs.micropython.org/en/latest/esp32/quickref.html#i2c-bus)

### GPIO Extender

The buttons and d-pad on the device are all connected through the GPIO extender, which communicates via I2C

To setup the GPIO extender:

```python
import mcpnew
io = mcpnew.MCP23017(i2c, address=0x20)
```

The GPIO extender has 16 pins, the buttons are on pins 4 - 7, while the d-pad is 8 - 11. These pins must first be setup as input pins, and their pullup resistors must be activated.

Then reading whether a button is pressed or not is simple.

```python
# pins for buttons
BUTTON_DOWN = 4
BUTTON_LEFT = 5
BUTTON_RIGHT = 6
BUTTON_UP = 7

# pins for d-pad directions
DPAD_UP = 8
DPAD_LEFT = 9
DPAD_RIGHT = 10
DPAD_DOWN = 11

pins = [4, 5, 6, 7, 8, 9, 10, 11]

for pin in pins:
    io.setup(pin, mcpnew.IN) # setups each pin as input
    io.pullup(pin, True)     # activates pull-up resistor for each pin

while True:
    if not io.input(BUTTON_UP): # True if not pressed, False if pressed
        print("Topmost button pressed")

    if not io.input(BUTTON_DOWN):
        print("Bottom button pressed")

    # etc.
```



### BME280 environmental sensor

The BME280 is able to measure temperature, humidity and atmospheric pressure.

To setup the component:

```python
import bme280_int

bme = bme280_int.BME280(i2c = i2c)
```

To quickly print the current values (temperature, humidity and pressure) in a readable format once could simply use:

```python
bme.values
```

One could also get the raw values, and then transform them manually:

```python
bmevals = bme.read_compensated_data()

temperature = bmevals[0]/100 # temperature in celsius
pressure = bmevals[1]//256   # pressure in pascal
humidity = bmevals[2] / 1024 # humidity in percent
```


### MPU-9250 motion sensor

The MPU-9250 is a 9-axis motion sensor. To setup the component:

```python
import mpu9250
mpu = mpu9250.MPU9250(i2c)
```

The unit can measure various things, and will return them as a tuple containing 3 float values (one for each axis)

```python
(ax, ay, az) = mpu.acceleration # acceleration in m/s^2
(gx, gy, gz) = mpu.gyro         # gyro values in rad/s
(mx, my, mz) = mpu.magnetic     # magnetic field values in µ-Tesla
```

### Display touch

The display has touch functionality through I2C. However, no micropython driver yet exists for this component.


# Analogue output and input

### The Speaker

The device has am inbuilt speaker, which takes an analogue signal to produce sound.

To get an analogue signal output we use the digital to analogue converter (DAC).

Here is an example to produce a simple sine wave sound:

```python
from machine import DAC, Pin
import math
import time

sh = Pin(2, Pin.OUT, Pin.PULL_UP)
sh.value(1)

dac = DAC(Pin(26))

# create a buffer containing a sine-wave
buf = bytearray(100)
for i in range(len(buf)):
    buf[i] = 128 + int(127 * math.sin(2 * math.pi * i / len(buf)))

bl = len(buf)
for i in range(9999999):
    dac.write(buf[i % bl])
```

### Microphone

The device also has a microphone. It is kind of the opposite of the speaker as it produces an analogue signal which then has to be converted to digital to be read by the microcontroller.

To do this we use the analogue to digital converter (ADC).

```python
from machine import Pin, ADC

mic = ADC(Pin(35))
mic.atten(ADC.ATTN_0DB)     # sets the attenuation for the microphone
mic.width(ADC.WIDTH_12BIT)  # sets the "ADC width", i.e. the bit resolution of the signal
while True:
    value = mic.read()
    val_8bit = int(value*(256/4096)) # gets the microphone output as a value between 0 - 255
    print(val_8bit)
```


# Example micropython programs

### Environmental sensor display [source](https://github.com/bytebarista/the_pad/blob/master/the_pad/demos/temperature.py)

Uses the display to show readings from the BME280 environmental sensor.

```python
import temperature

temperature.run()
```

### Snake game [source](https://github.com/bytebarista/the_pad/blob/master/the_pad/demos/snek.py)

A simple snake game written in micropython. Uses d-pad input and the display.

```python
import snek

snek.run()
```

### Tetris clone [source](https://github.com/bytebarista/the_pad/blob/master/the_pad/demos/tetrix.py)

A simple micropython tetris clone. D-pad to move bricks, left/right buttons to rotate bricks.

```python
import tetrix

tetrix.run()
```


# Exercizes

### Explore the thumbslide

* **The thumbslide** has many a quirk, and is not exemplified anywhere in this notebook. It has a dynamic range of "at rest" values for both x and y, which is not necessarily the same ranges. [ready-made thumbslide source](https://github.com/bytebarista/iot_workshop/blob/master/src/thumbslide.py)
  * You could make code to determine the state of the thumbslide to either be moved or not.
  * And/or you could calculate the angle it is held at *given* that it is moved.
  * Or, switch out the whole pad control for the Snake game with the thumbslide.

### Explore the speaker
* **The Speaker** can do a little bit more than just buzzzz uncomfortably.
  * The boot sequence could make a "boot complete" audio(-visual?) signal on completion.
  * The inputs could make different beeps on press ([note frequencies](http://pages.mtu.edu/~suits/notefreqs.html))
  * Snake and Tetrix are both silent gaming experiences, they could make use of some beeps and plings and buzzzzzes.
  * The sound could make use of a simple Low Frequency Oscillator ([LFO](https://en.wikipedia.org/wiki/Low-frequency_oscillation)) add-on to the example to give it a bit more "emotional range".

### Ball game exercize

A step-by-step exercize to make a simple micropython "ball game" can be found at [this link](https://github.com/bytebarista/iot_workshop/blob/master/Excercise%20-%20Ball%20game.md)

  
