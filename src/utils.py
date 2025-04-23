# Utils

import config, led, machine

async def log(msg: str):
    print(msg)

    import mqtt_handler
    if mqtt_handler.client:
        try:
            await mqtt_handler.client.publish(config.MQTT_LOG_TOPIC, msg, qos=0)
        except:
            print("Log publish failed")

def set_brightness(color, brightness):
    return tuple(int(c * brightness) for c in color)

async def sleep():
    try:
        await log("Going to sleep now...")
        led.turn_off()

        import mqtt_handler
        if mqtt_handler.client:
            mqtt_handler.client.close()
    finally:
        import esp32, intercom
        esp32.wake_on_ext0(pin=intercom.ringing_pin, level=esp32.WAKEUP_ANY_HIGH)
        machine.deepsleep()
