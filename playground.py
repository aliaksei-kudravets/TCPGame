import random
import time

class TeleTournir():
    def __init__(self):
        self.player_limit = 4
        self.questions = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k'} 
        self.accept = 'tak'
        self.decline = 'nie'
        self.answer_time = 5
        
    def exception_handler(self, exception):
        print('We have problem here {}'.format(exception))
        
    def get_5_questions(self) -> list():
        """return 3 random elements from questions"""
        return random.sample(self.questions, 3)

        
class Client():
    def __init__(self):
        self.isFirst = False
        self.count = 0
        self.isKicked = False
    



def wait_answer():
    start_time = time.time()
    print('IM WAIT ANSWER!')
    time.sleep(3)
    
    print("--- %s seconds ---" % (time.time() - start_time))
    

def event_loop():
    # W każdej z rund serwer rozsyła - 
    # zapytania do graczy i czeka na tego, który da poprawną odpowiedź najszybciej,
    t = TeleTournir()
    randomed_questions = t.get_5_questions()
    while randomed_questions:
        print(randomed_questions.pop())
        wait_answer()
        time.sleep(5)
    
    
            
        
        
event_loop()