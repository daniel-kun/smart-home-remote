import asyncio
import os
from bleak import discover, BleakClient
from dimmerhandler import DimmerHandler, AsyncIoScheduler
from gira_controller import GiraController

loop = asyncio.get_event_loop()

CHARACTERISTIC_UUID = '99ca7635-879d-4b08-bca1-0a8ba1ff0d47'
dimmerHandler = DimmerHandler(GiraController(), AsyncIoScheduler(loop))

def notify_receiver(sender, data):
    global dimmerHandler
    upDown = int.from_bytes(data, byteorder='little')
    if upDown == 1:
        dimmerHandler.button_down()
    else:
        dimmerHandler.button_up()
    print("Received notification #{}!".format(upDown))

async def run():
    global CHARACTERISTIC_UUID
    devices = await discover()
    for d in devices:
        print('Found {}'.format(d))
        if d.name == "ESP32" or d.name == os.getenv("SMARTHOMEREMOTE_BLE_SERVERNAME"):
            print("Connecting to {}".format(d))
            async with BleakClient(d.address, loop=loop) as client:
                print("Connected to {}".format(client))
                await client.start_notify(CHARACTERISTIC_UUID, notify_receiver)
                # Handle notifications while we are connected:
                while await client.is_connected():
                    print("Still alive, yay!")
                    await asyncio.sleep(5, loop=loop)

loop.run_until_complete(run())
