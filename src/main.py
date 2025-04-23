import asyncio, intercom, mqtt_handler, machine, utils

async def main():
    intercom.init()
    await mqtt_handler.setup()

    await utils.log("Booting up")

    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        await utils.log("Woke from deep sleep due to EXT0")

        if intercom.is_ringing():
            asyncio.create_task(intercom.handle_ringing())
            return # Prevent calling sleep
        
        await utils.log("Woke up, but no ringing signal detected.")
    else:
        await utils.log("Cold boot - sending discovery messages")
        await mqtt_handler.send_discovery()
        await asyncio.sleep(3)

    await utils.sleep()

try:
    asyncio.run(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()
except Exception as e:
    print(e)
    asyncio.run(utils.sleep())
