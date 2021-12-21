import asyncio

clients = list()

async def get_response(reader):
    data = await reader.read(100)
    message = data.decode()
    striped_text = message.strip()
    return striped_text

# TODO Реализовать механизм старта , первый сокет отправляет start 
# и остальным высылаются вопросы,  если игроки подключились, 
# а админ не стартовал - вопросы не высылаются
async def send_text(writer, message):
    text = "{}\n".format(message)
    writer.write(text.encode())
    await writer.drain()


async def event_loop(reader, writer):
    clients.append(writer)
    
    print(await get_response(reader))
    
    print('SEND BROADCATS')
    
    for ws in clients:
        await send_text(ws, 'TEST MESSAGE BROADCAST')
    
# Connection == отдельный цикл, по отдельности выполняются как бы

async def main():
    server = await asyncio.start_server(
        event_loop, '127.0.0.1', 4004)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())