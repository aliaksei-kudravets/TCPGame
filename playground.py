import asyncio
import random

clients_writers = []
clients_readers = []
responses = []
MAX_PLAYERS = 4
QUESTIONS_NUMBER = 7

client_answer = dict()
clients_without_answer = []

client_writer_score = dict()
client_writer_nick = dict()

questions = {'Polska jest większa od Nowej Zelandii?': 'tak',
             'Woda zamarza w 42 stopniach Fahrenheita?': 'nie',
             'W Szwajcarii obowiązują cztery języki urzędowe?': 'tak',
             'W finale Mistrzostw Świata 1974 w piłce nożnej zmierzyły się ze sobą reprezentacje Brazylii i Niemiec?': 'nie',
             'Średnia odległość Ziemi od Słońca to około 150 000 000 km?': 'tak',
             'Kość promieniowa to kość długa wchodząca w skład kości kończyn górnych?': 'nie',
             'Crvena Zvezda to klub piłkarski z siedzibą w Belgradzie?': 'tak',
             'Jedno z największych przedsiębiorstw na świecie, Sinopec, ma swoją siedzibę w Stanach Zjednoczonych?': 'nie',
             'Nie” to po hiszpańsku „No"?': 'tak',
             'Pierwszy król Polski, Bolesław Chrobry, był koronowany w 1033 roku?': 'nie',
             'Tanzania to państwo leżące w Ameryce Południowej?': 'nie',
             'Stambuł leży zarówno w Europie, jak i w Azji?': 'tak',
             'Kalendarzowa zima kończy się 21 marca?': 'tak'}

INSTRUCTION = 'Hej! Gra polega na tym, ze będziesz dostawal 7 pytan, odpowiedz na nich tak lub nie, masz na kazde 7 secund, poprawna odpowiedz to 1 pt, nie poprawna -2 pt!'

questions_pool = random.sample(questions.keys(), QUESTIONS_NUMBER)
question_pool_item = ''

players_score = [[] for _ in range(MAX_PLAYERS)]
is_more_then_5_sec = False


async def get_response(reader):
    data = await reader.read(256)
    message = data.decode()
    striped_text = message.strip()
    return striped_text


async def answers_matcher(client_text_answer: str, client_ws):
    """ we have key - question, we have answer - client text answer, 
    want to match client answer to correct answer in dict, 
    want to return number, correct = 1 pt, uncorect = -2 pt, if error  = 0 """

    print('q pool item is ', question_pool_item)
    correct_answer = questions.get(question_pool_item)
    print('correct answer is ', correct_answer)

    print(f'client send {client_text_answer}')

    if correct_answer == client_text_answer.lower():
        return 1

    if client_text_answer != 'tak' and client_text_answer != 'nie':
        await send_text(message='ERROR', writer=client_ws)
        return 0

    if correct_answer != client_text_answer.lower():
        return -2

def get_winner(players_score:list):
    res = -100
    for small_list in players_score:
        if len(small_list) != 0:
            
            tmp_sum = sum(small_list)
            
            if tmp_sum > res:
                res = tmp_sum
    
    return res

async def send_results(clients_writers):
    q_number = 0
    max_points = 0

    for client_ws in clients_writers:
        
        sum_of_points = sum(players_score[q_number])

    
        if sum_of_points >= max_points:
            max_points = sum_of_points

        await send_text(writer=client_ws,
                        message=f'Oto twoje wyniki calkiem : {sum_of_points}')

        await send_text(writer=client_ws,
                        message=f'A tutaj po pytaniam po koleje {players_score[q_number]}')
        if sum_of_points == max_points:
            await send_text(writer=client_ws, 
                            message=f'Max wynik to {sum_of_points}, wychodzi ze wygrales')
        if len(clients_writers) == 1:
            max_points == sum_of_points
        
        winner_point = get_winner(players_score)
        
        await send_text(writer=client_ws, message='Wygral gracz z {} punktem(ami)'.format(winner_point))
        
        await send_text(writer=client_ws, 
                        message='Koniec')
        
        q_number += 1
        
        # TODO for client writers score 
        # if sum(score) == winer point : send text (ws, wygral)


async def receive_broadcast_response(clients_readers, client_writers):
    """client writers need to add to list clients, 
    who dont send answer"""

    readers_writers: tuple = zip(clients_readers, client_writers)
    cl_id = 0
    for client_socket in readers_writers:
        reader = client_socket[0]
        writer = client_socket[1]
        try:
            text: str = await asyncio.wait_for(get_response(reader=reader),
                                               timeout=6)

            player_point = await answers_matcher(text.replace(' ', ''), client_ws=writer)
            tmp = players_score[cl_id]
            tmp.append(player_point)
            cl_id += 1
            
            global client_writer_score
            
            client_writer_score.update({reader: tmp})
            
            # print(players_score)
        except asyncio.TimeoutError:
            # clients_without_answer.append(writer)
            await send_text(writer=writer,
                            message='Sorki, nie dostałem odpowiedzi , timeout!')
        except IOError:
            print('ADMIN DISCONNECT')
            raise KeyboardInterrupt


async def send_text(writer, message):
    text = "{}\n".format(message)
    try:
        writer.write(text.encode())
        await writer.drain()
    except ConnectionResetError as e:
        print('CLIENT DISCONECTED {} '.format(writer))


async def send_broadcast_text(client_writers, text: str):
    for client in client_writers:
        await send_text(writer=client, message=text)


async def send_broadcast_question(clients_writers_list):
    '''also load dict writer : nick'''
    try:
        # print('QUESTIONS LIST IS' , questions_pool)
        global question_pool_item
        question_pool_item = questions_pool.pop()
        
        count = 0
        
        for ws in clients_writers_list:
            await send_text(writer=ws, message=question_pool_item)
            client_writer_nick.update({ws: "Uzytkownik {}".format(count)})
            count+=1
            print(client_writer_nick)
    except IndexError as e:
        # print('Index error in send broadcast questions')
        await send_results(clients_writers=clients_writers_list)

        question_pool_item = random.sample(questions.keys(), QUESTIONS_NUMBER)
        # print('NEW POOL IS', question_pool_item)
        raise KeyboardInterrupt
        # return True


async def admin_connection(reader, writer):
    await send_text(writer=writer,
                    message='jestes 1 , mozesz startowac gre , wpisz start')
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
        await send_broadcast_text(client_writers=clients_writers,
                                  text=INSTRUCTION)
        while True:
            try:
                is_end = await send_broadcast_question(clients_writers_list=clients_writers)
                print(is_end)

                if is_end:
                    # Close sockets
                    for writer in clients_writers:
                        writer.close()

                    break
            except ConnectionResetError as e:
                # print('admin disconnect!')
                print('CLIENT DISCONECTED {} '.format(writer))
                
            await receive_broadcast_response(clients_readers=clients_readers,
                                             client_writers=clients_writers)

            # for client_writer in clients_without_answer:
            #     await send_text(writer=client_writer, 
            #                     message='Sorki, nie dostałem odpowiedzi , timeout!')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server_gen = asyncio.start_server(
        event_loop, '127.0.0.1', 4011)

    server = loop.run_until_complete(server_gen)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        # print('CTRL C PRESS')
        loop.stop()  # Press Ctrl+C to stop
    finally:
        loop.stop()
