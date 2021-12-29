import asyncio
import random
import time
import itertools


clients_writers = []
clients_readers = [] 
responses = []
MAX_PLAYERS = 4

isEnd = False

clients_time_dict = dict()
clients_time_dict_1 = dict()
clients_time_dict_2 = dict()
clients_time_dict_3 = dict()


client_answer = dict()
clients_without_answer = []

client_writer_score = dict()

questions = {'pytanie1':'tak', 'pytanie2':'nie', 
                 'pytanie3':'tak', 'pytanie4':'nie', 
                 'pytanie5':'tak', 'pytanie6':'nie',
                 'pytanie7':'tak', 'pytanie8':'nie', 
                 'pytanie9':'tak', 'pytanie10':'nie'}

questions_pool = random.sample(questions.keys(), 3)
question_pool_item = ''

players_score = [[] for _ in range(MAX_PLAYERS)]
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

def answers_matcher(client_text_answer:str):
    """ we have key - question, we have answer - client text answer, 
    want to match client answer to correct answer in dict, 
    want to return number, correct = 1 pt, uncorect = -2 pt """
    print('q pool item is ', question_pool_item)
    correct_answer = questions.get(question_pool_item)
    print('correct answer is ', correct_answer)
    
    print(f'client send {client_text_answer}')
    print(type(client_text_answer))
    if correct_answer == client_text_answer.lower():
        return 1
    
    if client_text_answer != 'tak' and client_text_answer != 'nie':
        return "ERROR"
    
    if correct_answer != client_text_answer.lower():
        return -2
    
    # return -2
    
    
async def send_results(clients_writers):
    q_number = 0
    for client_ws in clients_writers:
        await send_text(writer=client_ws, message='Oto twoje wyniki:')
        await send_text(writer=client_ws, message = players_score[q_number])
        q_number+=1

async def receive_broadcast_response(clients_readers, client_writers):
    """client writers need to add to list clients, 
    who dont send answer"""
    
    readers_writers: tuple = zip(clients_readers, client_writers)
    cl_id = 0
    for client_socket in readers_writers:
        reader = client_socket[0]
        writer = client_socket[1]
        try:
            text:str = await asyncio.wait_for(get_response(reader=reader),
                                          timeout=10)
            # print('CLIENT SEND', text)
            player_point = answers_matcher(text.replace(' ', ''))
            players_score[cl_id].append(player_point)
            cl_id+=1
            print(players_score)
        except asyncio.TimeoutError:
            clients_without_answer.append(writer)
        

async def send_text(writer, message):
    text = "{}\n".format(message)
    writer.write(text.encode())
    await writer.drain()

async def send_broadcast_question(clients_writers):
        try:
            print('QUESTIONS LIST IS' , questions_pool)
            global question_pool_item
            question_pool_item = questions_pool.pop()
            for ws in clients_writers:
                await send_text(writer=ws, message=question_pool_item)
        except IndexError as e:
            print('Index error in send broadcast questions')
            await send_results(clients_writers=clients_writers)
            global isEnd
            isEnd = True
    
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
        # start = time.time()
        # count = -1
        while True:
            try:
                await send_broadcast_question(clients_writers=clients_writers)
            except ConnectionResetError as e:
                print('admin disconnect!')
            await receive_broadcast_response(clients_readers=clients_readers,
                                            client_writers=clients_writers)
                                       
            
            for client_writer in clients_without_answer:
                await send_text(writer=client_writer, 
                                message='Timeout! Be faster')
                    
            
  
    
async def main():
    server = await asyncio.start_server(
        event_loop, '127.0.0.1', 4008)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()
        if isEnd:
            server.close()

asyncio.run(main())