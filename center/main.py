import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import ssl
from aiohttp import web
from bleak import discover, BleakClient
from dimmerhandler import DimmerHandler, AsyncIoScheduler
from gira_controller import GiraController
from config import load_config

loop = asyncio.get_event_loop()

CHARACTERISTIC_UUID = '99ca7635-879d-4b08-bca1-0a8ba1ff0d47'
ble_name    = os.getenv("SMARTHOMEREMOTE_BLE_SERVERNAME")

def notify_receiver(sender, data, config):
    upDown = int.from_bytes(data[1:2], byteorder='little', signed=False)
    pin = int.from_bytes(data[0:1], byteorder='little', signed=False)
    if upDown == 1:
        if pin in config and config[pin] != None:
           config[pin].button_down()
    else:
        if pin in config and config[pin] != None:
            config[pin].button_up()
    print("Received notification #{}!".format(upDown))

async def run(config):
    global CHARACTERISTIC_UUID, ble_name
    print("Started BLE")
    while True:
        devices = await discover()
        for d in devices:
            print('Found {}'.format(d))
            if d.name == "ESP32" or d.name == ble_name:
                print("Connecting to {}".format(d))
                async with BleakClient(d.address, loop=loop) as client:
                    print("Connected to {}".format(client))
                    await client.start_notify(CHARACTERISTIC_UUID, lambda sender, data: notify_receiver(sender, data, config))
                    # Handle notifications while we are connected:
                    while await client.is_connected():
                        print("Still alive, yay!")
                        await asyncio.sleep(5, loop=loop)
        await asyncio.sleep(5, loop=loop)

async def start_ble_task(app, config):
    app['ble_task'] = asyncio.create_task(run(config))

if __name__ == '__main__':
    try:
        app = web.Application()
        scheduler = AsyncIoScheduler(loop)
        config = load_config(sys.argv[1], scheduler, app)
        print(config)
        app.on_startup.append(lambda app: start_ble_task(app, config))
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('cert.pem', 'key.pem')
        web.run_app(app, ssl_context=context)

    except KeyboardInterrupt:
        print("Bye bye")
