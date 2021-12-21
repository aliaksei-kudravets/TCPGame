import asyncio
import random
clients = []
questions_count = 0

isStarted = False
# TODO Высылать вопросы только после начала игры, 
# реализовать механизм ожидания ответа кто быстрее, если через 5 сек ответа нет - следующий вопрос 
 
     
# def parse_response(response:str):
#     tmp = response.strip()
#     if tmp == 'start':
#         return True
#     if tmp == 'tak':
#         print('client TAK')
#     if tmp == 'nie':
#         print('client NIE')    
    
        
        
async def get_response(reader):
    data = await reader.read(100)
    message = data.decode()
    striped_text = message.strip()
    # parse_response(striped_text)
    return striped_text


async def send_text(writer, message):
    text = "{}\n".format(message)
    writer.write(text.encode())
    await writer.drain()
    

async def get_user_data(writer):
    addr = writer.get_extra_info('peername')
    
    formated_client_adr = '{}:{}'.format(addr[0], addr[1])
    if formated_client_adr not in clients:
        clients.append(formated_client_adr)
    

async def event_loop(reader, writer):
    admin = False
    if len(clients) == 0:
        # its admin connections
        await get_user_data(writer)
        
        await send_text(writer, 'U ADMIN! SEND 1 TO START THE GAME')
        answer = await get_response(reader)
        if answer == 'start':
            admin = True
            
        
        
    if len(clients) == 4:
        # send error message, to much players
        await send_text(writer, 'sorry, many players')
        writer.close()
        
        
    else:
        # send questions
        
        await get_user_data(writer)
        questions = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k'}
        q = random.sample(questions, 3)
        
        while q:
            await send_text(writer, q.pop())
            await get_response(reader)
            # await send_text(writer, 'play on next game, this game starts or close')  
              
            if len(q) == 0:
                await send_text(writer, 'GG')
                writer.close()
                break
        
    
    
async def main():
    server = await asyncio.start_server(
        event_loop, '127.0.0.1', 8889)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())