import asyncio
import websockets
import json

#from_web = asyncio.Queue()
#to_web = asyncio.Queue()


async def read_socket(reader):
    while True:
        data = await reader.readline()
        try:
            message = int(data.decode())
        except ValueError:
            message = data.decode()
        print("From SocketServer To WebServer: %r" % message)
        await to_web.put(data)
        #await asyncio.sleep(0.5)


async def write_socket(writer):
    brightness = 10
    step = 5
    while True:
        brightness = await from_web.get()
        writer.write(brightness)
        await writer.drain()
        print(f"From WebServer To SocketServer {brightness}")
        #await asyncio.sleep(0.5)


async def handle_echo(reader, writer):
    print("New SocketServer connection")
    loop.create_task(read_socket(reader))
    loop.create_task(write_socket(writer))


async def read_websocket(websocket, path):
    async for message in websocket:
        data = message;
        print(f"From FrontEnd To WebServer: {data}")
        if data != "":
            data = json.loads(data)
            data = str(data['brightness']) + '\n'
            await from_web.put(data.encode())
            #            data = str(message)
            #            await from_web.put(data)

            # await asyncio.sleep(0.5)


async def write_websocket(websocket, path):
    while True:
        data = await to_web.get()
        await websocket.send(json.dumps({"value": int(data)}))
        print(f"From WebServer To FrontEnd: {data}")
        # await asyncio.sleep(0.5)


async def counter(websocket, path):
    print("New FrontEnd connection")
    consumer_task = asyncio.ensure_future(
        read_websocket(websocket, path))
    producer_task = asyncio.ensure_future(
        write_websocket(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


loop = asyncio.get_event_loop()
from_web = asyncio.Queue()
to_web = asyncio.Queue()
coro = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
web = websockets.serve(counter, "127.0.0.1", 8887, loop=loop)

server1 = loop.run_until_complete(coro)
server2 = loop.run_until_complete(web)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server1.sockets[0].getsockname()))
print('Serving on {}'.format(server2.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server1.close()
loop.run_until_complete(server1.wait_closed())
server2.close()
loop.run_until_complete(server2.wait_closed())
loop.close()
