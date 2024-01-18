from src.connections import find_cpod, sendTriggerCPOD
from datetime import datetime
import pyxid2

devices = pyxid2.get_xid_devices()
dev = devices[0]
sendTriggerCPOD(dev, 5, 500)
sendTriggerCPOD(dev, 5, 500)
sendTriggerCPOD(dev, 5, 500)
sys.exit()

def test_trigger_output(device, duration):
    send_time = datetime.now()
    sendTriggerCPOD(device, 5, duration)
    received = datetime.now()
    print(f'Sent:{send_time}, Received:{received}, Difference:{received-send_time}')

for dur in [1,2,3]:
    test_trigger_output(device, dur)

found, devices = find_cpod()
print(found)
if not found:
    sys.exit()

print(devices)
