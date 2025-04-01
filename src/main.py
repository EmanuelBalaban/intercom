import time, machine, neopixel

import config

np = neopixel.NeoPixel(machine.Pin(config.NEO_PIXEL_PIN, machine.Pin.OUT), 1)

ringing_pin = machine.Pin(config.RINGING_PIN, machine.Pin.IN)
talk_pin = machine.Pin(config.TALK_PIN, machine.Pin.OUT)
open_pin = machine.Pin(config.OPEN_PIN, machine.Pin.OUT)

def main():
    talk_pin.off()
    open_pin.off()

    np[0] = set_brightness((0, 0, 0), 0.0)  # Black
    np.write()

    while True:
        time.sleep_ms(100)

        print("Ringing pin value: ", ringing_pin.value())

        if is_ringing():
            print("Intercom is ringing!")

            np[0] = set_brightness((255, 0, 0), 0.1)  # Red
            np.write()

            print("Opening!")

            open()

            print("Door is open!")

            time.sleep_ms(2000)

            np[0] = set_brightness((0, 0, 0), 0.0)  # Black
            np.write()

def is_ringing() -> bool:
    return ringing_pin.value() == 1

def open():
    # Reset pins
    talk_pin.off()
    open_pin.off()
    time.sleep_ms(250)

    # Talk
    talk_pin.on()
    time.sleep_ms(1000)
    talk_pin.off()
    time.sleep_ms(500)

    # Open
    open_pin.on()
    time.sleep_ms(1000)
    open_pin.off()

def set_brightness(color, brightness):
    """ Adjust color with the given brightness. """

    return tuple(int(c * brightness) for c in color)

main()