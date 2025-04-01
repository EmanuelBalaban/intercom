import machine

# Power neopixel
neo_pixel_power_pin = 2
led_pwr = machine.Pin(neo_pixel_power_pin, machine.Pin.OUT)
led_pwr.value(0)