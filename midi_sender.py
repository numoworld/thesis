import rtmidi
from rtmidi.midiconstants import CONTROL_CHANGE


class MidiSender:
    def __init__(self, port=0) -> None:
        self.midiout = rtmidi.MidiOut()
        self.midiout.open_port(port)

    def bind_control(self, control_id):
        print(control_id)
        self.control_change(control_id, 0)

    def control_change(self, control_id, value):
        self.midiout.send_message([CONTROL_CHANGE, control_id, value*127])