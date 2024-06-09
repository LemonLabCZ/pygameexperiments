from src.connections import sendTrigger
from datetime import datetime

def test_trigger_output(duration, threadTimeout):
    send_time = datetime.now()
    sendTrigger(5, 'COM4', duration, threadTimeout)
    received = datetime.now()
    print(f'Sent:{send_time}, Received:{received}, Difference:{received-send_time}')
    print(f'The process took {round((received-send_time).total_seconds() - duration, 3)}s longer than needed' )


for i in [1,2,3]:
    test_trigger_output(i)

test_trigger_output(0.01, 3)