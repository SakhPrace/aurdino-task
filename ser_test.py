import asyncio
import aioserial


async def socket_reader(reader, to_serial):
    while True:
        data = await reader.readline()
        msg = data.decode()
        if msg != "":
            msg = f'From SocketServer To Aurdino: {msg}'
            print(msg)
            await to_serial.put(data)


async def socket_writer(writer: asyncio.StreamWriter, from_serial):
    while True:
        data = await from_serial.get()
        writer.write(data)
        await writer.drain()


async def serial_reader(aio_port: aioserial.AioSerial, from_serial):
    while True:
        data = await aio_port.readline_async()
        if data != "":
            try:
                brightness = int(data.decode())
            except ValueError:
                brightness = data.decode()
            print(f"From Aurdino To SocketServer: {brightness}")
            await from_serial.put(data)


async def serial_writer(aio_port: aioserial.AioSerial, to_serial):
    while True:
        data = await to_serial.get()

        await aio_port.write_async(data)


async def init_all(port=8888):
    # Open serial port
    ser = aioserial.AioSerial(port='/dev/ttyUSB0', baudrate=9600, timeout=1)
    print('Port opened')

    # Open socket

    reader, writer = await asyncio.open_connection(
        '127.0.0.1', port)
    print('Socket opened')
    # Create queues
    from_serial = asyncio.Queue()
    to_serial = asyncio.Queue()

    # Run everything
    await asyncio.gather(serial_reader(ser, from_serial),
                         serial_writer(ser, to_serial),
                         socket_reader(reader, to_serial),
                         socket_writer(writer, from_serial))


asyncio.run(init_all())
