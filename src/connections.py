import serial
import pyxid2
import threading
import pylink
import time

def find_cpod():
    try:
        devices = pyxid2.get_xid_devices()
    except:
        print("No XID-devices detected")
        return False, None
    return len(devices) > 0, devices


# send a trigger via CEDRUS cPOD to NIRx devices
def sendTriggerCPOD(device, value, duration):
    # input variable:
    # device: CEDRUS cPOD - object
    # value: int trigger
    # duration: pulse duratin in milliseconds
    bitList = list(str(bin(value)))
    activeLines = []
    bitCounter = 0
    for ii in range(len(bitList)-1,1,-1):
        bitCounter += 1
        if bitList[ii] == '1':
            activeLines.append(bitCounter)
    
    device.activate_line(lines = activeLines)
    time.sleep(duration/1000)
    device.clear_all_lines()    


def sendTrigger(decTriggerVal, com_port, duration = 0.01, threadTimeout = 1, delay = None):
    Connected = True
    hexTriggerVal = int(hex(decTriggerVal), 16)
    def ReadThread(port):
        while Connected:
            if port.inWaiting() > 0:
                print ("0x%X"%ord(port.read(1)))

    if delay is not None and delay > 0:
        time.sleep(delay)
    port = serial.Serial(com_port, baudrate=2000000)
    thread = threading.Thread(target=ReadThread, args=(port,))
    thread.start()
    port.write([hexTriggerVal])
    time.sleep(duration)
    port.write([0x00])
    Connected = False
    thread.join(threadTimeout)
    port.close()

## Eyetracker
## ==========================

def find_eyetracker():
    try:
        el_tracker = pylink.EyeLink("100.1.1.1")
        return True, el_tracker
    except RuntimeError as error:
        print('ERROR:', error)
        return False, None
