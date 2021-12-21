import asyncio

clients = []   

isStarted = False

# TODO Высылать вопросы только после начала игры, 
# реализовать механизм ожидания ответа кто быстрее, если через 5 сек ответа нет - следующий вопрос 
 
     
def parse_response(response:str):
    tmp = response.strip()
    if int(tmp) == 1:
        print('GAME STARTS')
        isStarted = True
    if tmp == 'tak':
        print('client TAK')
    if tmp == 'nie':
        print('client NIE')    
    # else:
    #     print('response is ', response)
        
        
async def get_response(reader):
    data = await reader.read(100)
    message = data.decode()
    striped_text = message.strip()
    parse_response(striped_text)
    print(striped_text)
    print(clients)
    return striped_text


async def send_question(writer, message):
    text = "{}\n".format(message)
    writer.write(text.encode())
    await writer.drain()
    

async def get_user_data(writer):
    addr = writer.get_extra_info('peername')
    
    formated_client_adr = '{}:{}'.format(addr[0], addr[1])
    if formated_client_adr not in clients:
        clients.append(formated_client_adr)
    

async def event_loop(reader, writer):
    if len(clients) == 0:
        # its admin connections
        await get_user_data(writer)
        admintPermission = True
        await send_question(writer, 'U ADMIN! SEND 1 TO START THE GAME')
        await get_response(reader)
        
    if len(clients) == 4:
        # send error message, to much players
        await send_question(writer, 'sorry, many players')
        writer.close()
        
        
    else:
        # send questions
        await get_user_data(writer)
        await send_question(writer, 'first question is')
        await get_response(reader)
        await get_response(reader)
        await get_response(reader)
        
    
    
async def main():
    server = await asyncio.start_server(
        event_loop, '127.0.0.1', 8866)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())