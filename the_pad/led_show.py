
import utime

from led_lights import setup_leds, LEDs, write_LED_CDS, write_shutoff_frame,\
    _write_start_frame, _write_LED_frame, _write_end_frame


def run():
    print("Running LED show...", end="")
    setup_leds()

    brightness = 10
    LEDs[0]['brightness'] = brightness
    LEDs[1]['brightness'] = brightness
    LEDs[2]['brightness'] = brightness
    LEDs[3]['brightness'] = brightness

    def _rainbow_update_leds(i):
        LEDs[0]['blue'] = i + 1
        LEDs[0]['green'] = i + 144
        LEDs[0]['red'] = i

        LEDs[1]['blue'] = i + 34
        LEDs[1]['green'] = i
        LEDs[1]['red'] = i

        LEDs[2]['blue'] = i
        LEDs[2]['green'] = i
        LEDs[2]['red'] = i + 50

        LEDs[3]['blue'] = 0
        LEDs[3]['green'] = i + 200
        LEDs[3]['red'] = i

    c = 5000
    cr = range(c)
    for i in cr:
        _rainbow_update_leds(i)
        write_LED_CDS(LEDs)
        utime.sleep_ms(6)

    utime.sleep_ms(800)

    shutoff_fade_speed = 200
    sr = range(shutoff_fade_speed)
    for i in sr:
        bright = int(brightness - i*0.072)
        _write_start_frame()
        _write_LED_frame(bright, blue=c + 1, green=c + 144, red=c)
        _write_LED_frame(bright, blue=c + 34, green=c, red=c)
        _write_LED_frame(bright, blue=c, green=c, red=c + 50)
        _write_LED_frame(bright, blue=0, green=c + 200, red=c)
        _write_end_frame()
        utime.sleep_ms(4)
        if bright <= 0.0:
            break

    write_shutoff_frame()
    print("done!")