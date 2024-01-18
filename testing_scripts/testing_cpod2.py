
import pyxid2
import time

# get a list of all attached XID devices
devices = pyxid2.get_xid_devices()

dev = devices[0] # get the first device to use
print(dev)

#dev.get_pulse_table_bitmask()
#dev.is_pulse_table_running()

dev.set_pulse_duration(300)
#dev.clear_all_lines()