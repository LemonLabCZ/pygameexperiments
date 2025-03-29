import serial
import pyxid2
import threading
import pylink
import time


def sendTrigger(decTriggerVal, com_port, duration = 0.01, threadTimeout = 1):
    Connected = True
    hexTriggerVal = int(hex(decTriggerVal), 16)
    def ReadThread(port):
        while Connected:
            if port.inWaiting() > 0:
                print ("0x%X"%ord(port.read(1)))

    port = serial.Serial(com_port)
    # Start the read thread
    thread = threading.Thread(target=ReadThread, args=(port,))
    thread.start()
    # Set the port to an initial state
    port.write([hexTriggerVal])
    time.sleep(duration)
    port.write([0x00])
    # Reset the port to its default state
    # Terminate the read thread
    Connected = False
    thread.join(threadTimeout)
    # Close the serial port
    port.close()


# Test 1:
sendTrigger(5, "COM3", 0.1)


# Test 2:
for i in range(20):
    port = serial.Serial("COM3")
    port.write([0x01])
    time.sleep(0.1)
    port.write([0x00])
    port.close()
    time.sleep(1)