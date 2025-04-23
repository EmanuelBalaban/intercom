# Mqtt logic

import config, asyncio, ubinascii, machine, utils, intercom
from lib.mqtt_as import MQTTClient, config as mqtt_config

client: MQTTClient | None = None

async def messages(client: MQTTClient):
    async for topic, msg, retained in client.queue:
        await asyncio.sleep(0) # Allow other instances to be scheduled

        await utils.log("{}: {}".format(topic, msg))
        
        if topic == config.MQTT_OPEN_DOOR_TOPIC and msg == b"PRESS":
            asyncio.create_task(intercom.handle_open_command())

async def up(client: MQTTClient): # (re)connection
    while True:
        await client.up.wait()
        client.up.clear()

        await utils.log("Subscribing to topics...")

        # Subscribe to topics
        await client.subscribe(config.MQTT_OPEN_DOOR_TOPIC, qos=1)

async def setup():
    global client

    # Configure mqtt_as
    mqtt_config['ssid'] = config.WIFI_SSID
    mqtt_config['wifi_pw'] = config.WIFI_PASSWD
    mqtt_config['client_id'] = ubinascii.hexlify(machine.unique_id()).decode()
    mqtt_config['server'] = config.MQTT_SERVER
    mqtt_config['user'] = config.MQTT_USER
    mqtt_config['password'] = config.MQTT_PASSWD
    mqtt_config['ssl'] = True
    mqtt_config['ssl_params'] = {'cert_reqs': 0}
    mqtt_config['will'] = (config.MQTT_LOG_TOPIC, 'offline', True, 0)
    mqtt_config['queue_len'] = 10

    client = MQTTClient(mqtt_config)

    try:
        await client.connect(quick=True) # Skip WiFi check
    except OSError:
        client = None
        await utils.log("Connection failed.")
        return

    asyncio.create_task(up(client))
    asyncio.create_task(messages(client))

async def send_discovery():
    if client is None:
        return

    await utils.log("Sending discovery messages...")

    import json

    try:
        for topic, payload in [
            (config.MQTT_RINGING_DISCOVERY_TOPIC, config.MQTT_RINGING_DISCOVERY_PAYLOAD),
            (config.MQTT_OPEN_DOOR_DISCOVERY_TOPIC, config.MQTT_OPEN_DOOR_DISCOVERY_PAYLOAD),
        ]:
            await client.publish(topic, json.dumps(payload), qos=1, retain=True)
    except Exception as e:
        await utils.log(f"Discovery error: {e}")
