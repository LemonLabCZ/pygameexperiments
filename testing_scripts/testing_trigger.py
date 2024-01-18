from src.connections import sendTrigger, find_cpod
from datetime import datetime

def test_trigger_output(duration):
    send_time = datetime.now()
    sendTrigger(5, 'COM8', duration)
    received = datetime.now()
    print(f'Sent:{send_time}, Received:{received}, Difference:{received-send_time}')

for i in [1,2,3]:
    test_trigger_output(i)
