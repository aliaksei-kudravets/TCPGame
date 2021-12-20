from playground import TeleTournir
from time import sleep
def test_random():
    t = TeleTournir()
    randomed_questions = t.get_5_questions()
    print(randomed_questions)
    
while True:
    test_random()
    sleep(2)