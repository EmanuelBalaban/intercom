# Intercom logic (ringing, talk, open door)

import config, machine, asyncio, led, utils, mqtt_handler

ringing_pin = machine.Pin(config.RINGING_PIN, machine.Pin.IN)
talk_pin = machine.Pin(config.TALK_PIN, machine.Pin.OUT, value=0)
open_pin = machine.Pin(config.OPEN_PIN, machine.Pin.OUT, value=0)

talking: bool = False
opening: bool = False

# Hard sleep timer in case IRQ doesn't work as expected
sleep_timer = machine.Timer(1) # Hardware timer 1

def init():
    talk_pin.off()
    open_pin.off()

    # Use IRQ to detect if the door was opened or not
    ringing_pin.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=ringing_irq)

def ringing_irq(pin: machine.Pin):
    asyncio.run(utils.log("IRQ for ringing pin: {}".format(pin.value())))

    if is_ringing():
        asyncio.create_task(handle_ringing())
    else:
        if mqtt_handler.client:
            asyncio.run(mqtt_handler.client.publish(config.MQTT_RINGING_TOPIC, "OFF", qos=1))

        if opening:
            asyncio.run(utils.log("Door is open!"))
        else:
            asyncio.run(utils.log("Dismissed or opened using old intercom..."))

        asyncio.create_task(utils.sleep())

async def handle_ringing():
    """ Handles the ringing event. Called after wakeup and when IRQ is triggered on rising edge. """

    # Reset flags
    global talking, opening
    talking = False
    opening = False

    await utils.log("Door is ringing!")
    led.turn_on()
    led.show_red()

    # Send ringing notification
    if mqtt_handler.client:
        await mqtt_handler.client.publish(config.MQTT_RINGING_TOPIC, "ON", qos=1)
    
    # TODO: handle physical buttons

    # Unanswered call
    sleep_timer.init(mode=machine.Timer.ONE_SHOT, period=60000, callback=_sleep_callback)

def _sleep_callback():
    asyncio.run(utils.sleep())

async def handle_open_command():
    """ Handles the open event. Called by the MQTT handler when receiving the OPEN command. """

    sleep_timer.deinit()

    global opening
    opening = True

    await utils.log("Opening door!")

    await press_talk()
    await asyncio.sleep_ms(500)
    await press_open()

def is_ringing():
    return ringing_pin.value() == 1

async def press_talk():
    global talking

    if talking:
        await utils.log("Talk was already pressed.")
        return

    talking = True
    await utils.log("Pressing talk...")

    talk_pin.on()
    await asyncio.sleep_ms(1000)
    talk_pin.off()

async def press_open():
    await utils.log("Pressing open...")

    open_pin.on()
    await asyncio.sleep_ms(1000)
    open_pin.off()
