import time
import rtmidi
from rtmidi.midiconstants import CONTROL_CHANGE

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

# here we're printing the ports to check that we see the one that loopMidi created.
# In the list we should see a port called "loopMIDI port".

# Attempt to open the port
if available_ports:
    midiout.open_port(1)
else:
    midiout.open_virtual_port("My virtual output")

controller1 = [CONTROL_CHANGE, 1, 56]
controller2 = [CONTROL_CHANGE, 1, 25]
controller3 = [CONTROL_CHANGE, 1, 0]

midiout.send_message(controller1)
time.sleep(1)
# I tried running the script without having to invoke the sleep function but it doesn't work.
# If someone could enlighten me as to why this is, I'd be more than grateful.
midiout.send_message(controller2)
time.sleep(1)
# I tried running the script without having to invoke the sleep function but it doesn't work.
# If someone could enlighten me as to why this is, I'd be more than grateful.
midiout.send_message(controller3)

del midiout