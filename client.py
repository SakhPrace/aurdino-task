import asyncio
import websockets


async def websocket_reader(websocket):
    while True:
        data = await websocket.recv()
        message = data.decode()
        print(f"From WebServer: {message}")
        #await asyncio.sleep(0.2)


async def websocket_writer(websocket):
    brightness = 10
    step = 5
    while True:
        brightness += step
        data = (str(brightness) + '\n').encode()
        if brightness == 0 or brightness == 255:
            step = -step

        await websocket.send(data)
        print(f"To WebServer: {data}")
        await asyncio.sleep(0.5)


async def init_all():
    uri = "ws://127.0.0.1:8887"
    async with websockets.connect(uri) as websocket:
        await asyncio.gather(websocket_reader(websocket), websocket_writer(websocket))

loop = asyncio.get_event_loop()
loop.run_until_complete(init_all())
loop.run_forever()
