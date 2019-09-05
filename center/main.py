import asyncio
from bleak import discover, BleakClient

CHARACTERISTIC_UUID = '99ca7635-879d-4b08-bca1-0a8ba1ff0d47'

def notify_receiver(sender, data):
    print("Received notification #{}!".format(int.from_bytes(data, byteorder='little')))

async def run():
    global CHARACTERISTIC_UUID
    devices = await discover()
    for d in devices:
        print('Found {}'.format(d))
        if d.name == "ESP32":
            print("Connecting to {}".format(d))
            async with BleakClient(d.address, loop=loop) as client:
                print("Connected to {}".format(client))
                await client.start_notify(CHARACTERISTIC_UUID, notify_receiver)
                # Handle notifications while we are connected:
                while await client.is_connected():
                    print("Still alive, yay!")
                    await asyncio.sleep(5, loop=loop)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
