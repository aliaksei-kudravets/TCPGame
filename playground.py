import asyncio
import random
import time

class Game():
    def __init__(self) -> None:
        self.questions = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k'}

    def get_random_questions_set(self):
        return random.sample(self.questions, 3)
    
    def return_by_1(self):
        for i in self.questions:
            yield i


clients_writers = []
clients_readers = [] 
responses = []


clients_time_dict = dict()
clients_time_dict_1 = dict()
clients_time_dict_2 = dict()
clients_time_dict_3 = dict()


questions = {'a':'tak', 'b':'nie', 
                 'c':'tak', 'd':'nie', 
                 'e':'tak', 'f':'nie',
                 'g':'tak', 'h':'nie', 
                 'j':'ta', 'k':'nie'}

q = random.sample(questions.keys(), 3)

# Словарь клиент-время ответа

is_more_then_5_sec = False

def get_winner_in_clients(clients_dicts):
    
    for key, value in clients_dicts.items():
        winner = value
        for time in clients_dicts.values():
            if time > winner:
                winner == time
    return winner
        

async def get_response(reader):   
    data = await reader.read(100)
    message = data.decode()
    striped_text = message.strip()
    return striped_text

async def receive_broadcast_response(clients_readers):
    client_id = 0
    for ws in clients_readers:
        start = time.time()
        await get_response(ws)
        stop = time.time() - start
        clients_time_dict[client_id] = stop
        # if client_id == 0:
        #     clients_time_dict_1[client_id] = stop
        # if client_id == 1:
        #     clients_time_dict_2[client_id] = stop
        # if client_id == 2:
        #     clients_time_dict_3[client_id] = stop
        
        
            
        client_id +=1
        

async def send_text(writer, message):
    text = "{}\n".format(message)
    writer.write(text.encode())
    await writer.drain()

async def send_broadcast_question(writer, clients_writers):
    if q:
        try:
            print('QUESTIONS LIST IS' , q)
            question = q.pop()
            for ws in clients_writers:
                await send_text(writer=ws, message=question)
        except IndexError as e:
            pass
    
async def admin_connection(reader, writer):
    admin_text = await get_response(reader=reader)
    if admin_text == 'start':
        return True
    return False
    

async def event_loop(reader, writer):
    
    
    clients_writers.append(writer)
    clients_readers.append(reader)
    status = False
    
    if len(clients_writers) == 1:
        status = await admin_connection(reader=reader, writer=writer)
        
    if status:
        start = time.time()
        count = -1
        while True:
            await send_broadcast_question(writer=writer, clients_writers=clients_writers)
            await receive_broadcast_response(clients_readers=clients_readers)
            
            print('ROUND {} is end'.format(count))
            count+=1
            
            if count == 0:
                print(clients_time_dict)
                print()
                print('WINNER TIME IS ', get_winner_in_clients(clients_time_dict))
                
            
            if count == 1:
                print(clients_time_dict)
                print('WINNER TIME IS ', get_winner_in_clients(clients_time_dict))
  
    
async def main():
    server = await asyncio.start_server(
        event_loop, '127.0.0.1', 4008)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())