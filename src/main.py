import esp32
import time, machine, neopixel, ubinascii, json
import config
from umqtt.simple import MQTTClient

# Neopixel pins
led_pwr = machine.Pin(config.NEO_PIXEL_POWER_PIN, machine.Pin.OUT, value=0)
np = neopixel.NeoPixel(machine.Pin(config.NEO_PIXEL_DATA_PIN, machine.Pin.OUT), 1)

# Intercom pins
ringing_pin = machine.Pin(config.RINGING_PIN, machine.Pin.IN)
talk_pin = machine.Pin(config.TALK_PIN, machine.Pin.OUT, value=0)
open_pin = machine.Pin(config.OPEN_PIN, machine.Pin.OUT, value=0)

client: MQTTClient | None = None
should_open_door: bool = False

def main():
    led_pwr.value(0)
    talk_pin.off()
    open_pin.off()

    configure_mqtt_client()
    log("Booting up!")

    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        log("Woke from deep sleep due to EXT0")

        if is_ringing():
            handle_ringing()
        else:
            log("Woke up, but no ringing signal detected.")
    else:
        log("Cold boot - setting up wakeup sources")
        send_discovery_messages()
        setup_wakeup()

    # At the end, go to sleep
    deep_sleep()

def setup_wakeup():
    esp32.wake_on_ext0(pin=ringing_pin, level=esp32.WAKEUP_ANY_HIGH)
    time.sleep_ms(5000)

def deep_sleep():
    log("Going to sleep now...")
    led_pwr.value(0)
    machine.deepsleep()

def handle_ringing():
    if client is None:
        log("Something went wrong!")
        return
    
    log("Ringing!")
    led_pwr.value(1)
    np[0] = set_brightness((255, 0, 0), 0.1)  # Red
    np.write()

    client.publish(config.MQTT_RINGING_TOPIC, "ON")
    client.check_msg()

    log("Waiting for open command...")
    while is_ringing() and not should_open_door:
        try:
            client.check_msg()
        except OSError as e:
            log(f"MQTT error: {e}")
            break

    client.check_msg()

    if should_open_door:
        open()

    np[0] = set_brightness((0, 0, 0), 0.0)  # Black
    np.write()

def open():
    log("Opening!")

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

    log("Door is open!")

def is_ringing() -> bool:
    return ringing_pin.value() == 1

def set_brightness(color, brightness):
    """ Adjust color with the given brightness. """
    return tuple(int(c * brightness) for c in color)

def mqtt_callback(topic, msg):
    global should_open_door
    if topic == config.MQTT_OPEN_DOOR_TOPIC and msg == b"PRESS":
        log("Received OPEN command!")
        should_open_door = True

def configure_mqtt_client():
    global client

    try:
        log("Connecting to MQTT broker...")

        import ssl
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.verify_mode = ssl.CERT_NONE

        client_id = ubinascii.hexlify(machine.unique_id())
        client = MQTTClient(
            client_id,
            server=config.MQTT_SERVER,
            user=config.MQTT_USER,
            password=config.MQTT_PASSWD,
            keepalive=60,
            ssl=ssl_context)
        client.connect()
        client.set_callback(mqtt_callback)
        client.subscribe(config.MQTT_OPEN_DOOR_TOPIC)

        log("Connected to MQTT broker!")
    except OSError as e:
        print(e)
        log("Failed to connect. Restarting...")
        time.sleep(3)
        machine.reset()    

def send_discovery_messages():
    if client is None:
        return

    log("Sending discovery messages..")
    for (topic, payload) in [
        (config.MQTT_RINGING_DISCOVERY_TOPIC, config.MQTT_RINGING_DISCOVERY_PAYLOAD),
        (config.MQTT_OPEN_DOOR_DISCOVERY_TOPIC, config.MQTT_OPEN_DOOR_DISCOVERY_PAYLOAD),
        ]:
        discovery_message = json.dumps(payload)

        client.publish(topic, discovery_message.encode(), retain=True)
        client.check_msg()

def log(msg: str):
    print(msg)
    if client is not None:
        try:
            client.publish(config.MQTT_LOG_TOPIC, msg)
            client.check_msg()
        except:
            print('Unable to send log message')


try:
    main()
except:
    print('Something unexpected happened!')
    machine.reset()