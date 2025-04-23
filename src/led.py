# LED logic

import neopixel, config, machine, utils

led_pwr = machine.Pin(config.NEO_PIXEL_POWER_PIN, machine.Pin.OUT, value=0)
np = neopixel.NeoPixel(machine.Pin(config.NEO_PIXEL_DATA_PIN), 1)

def turn_on():
    led_pwr.value(1)

def turn_off():
    led_pwr.value(0)

def show_red():
    np[0] = utils.set_brightness((255, 0, 0), 0.1)
    np.write()

def show_black():
    np[0] = (0, 0, 0)
    np.write()