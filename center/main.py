import asyncio
import os
from bleak import discover, BleakClient
from dimmerhandler import DimmerHandler, AsyncIoScheduler
from gira_controller import GiraController

loop = asyncio.get_event_loop()

CHARACTERISTIC_UUID = '99ca7635-879d-4b08-bca1-0a8ba1ff0d47'

scheduler = AsyncIoScheduler(loop)

serverIp    = os.getenv("SMARTHOMEREMOTE_SERVERIP")
dpDim1      = os.getenv("SMARTHOMEREMOTE_DP_DIM1")
dpOnOff1    = os.getenv("SMARTHOMEREMOTE_DP_ONOFF1")
dpDim2      = os.getenv("SMARTHOMEREMOTE_DP_DIM2")
dpOnOff2    = os.getenv("SMARTHOMEREMOTE_DP_ONOFF2")
token       = os.getenv("SMARTHOMEREMOTE_APITOKEN")
ble_name    = os.getenv("SMARTHOMEREMOTE_BLE_SERVERNAME")

dimmerHandler = {
    22: DimmerHandler(GiraController(serverIp, token, dpDim1, dpOnOff1), scheduler),
    21: DimmerHandler(GiraController(serverIp, token, dpDim2, dpOnOff2), scheduler)
}

def notify_receiver(sender, data):
    global dimmerHandler
    upDown = int.from_bytes(data[1:2], byteorder='little', signed=False)
    pin = int.from_bytes(data[0:1], byteorder='little', signed=False)
    if upDown == 1:
        if pin in dimmerHandler:
           dimmerHandler[pin].button_down()
    else:
        if pin in dimmerHandler:
            dimmerHandler[pin].button_up()
    print("Received notification #{}!".format(upDown))

async def run():
    global CHARACTERISTIC_UUID, ble_name
    devices = await discover()
    for d in devices:
        print('Found {}'.format(d))
        if d.name == "ESP32" or d.name == ble_name:
            print("Connecting to {}".format(d))
            async with BleakClient(d.address, loop=loop) as client:
                print("Connected to {}".format(client))
                await client.start_notify(CHARACTERISTIC_UUID, notify_receiver)
                # Handle notifications while we are connected:
                while await client.is_connected():
                    print("Still alive, yay!")
                    await asyncio.sleep(5, loop=loop)

loop.run_until_complete(run())
