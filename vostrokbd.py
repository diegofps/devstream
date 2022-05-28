from utils import BaseConsumer, info, warn
from evdev import ecodes as e


MACRO_KEYBOARDS = [
    "Arduino LLC Arduino Leonardo", 
]

INPUT_KEYBOARDS = [
    "AT Translated Set 2 keyboard", 
    "CORSAIR CORSAIR K63 Wireless USB Receiver Keyboard", 
]

TARGET_DEVICE = INPUT_KEYBOARDS + MACRO_KEYBOARDS

MACRO_PLAY   = {
    e.KEY_R:"MA", e.KEY_Q:"MB", e.KEY_P:"MC", e.KEY_O:"MD", e.KEY_N:"ME", e.KEY_M:"MF", 
    e.KEY_9:"MG", e.KEY_8:"MH", e.KEY_7:"MI", e.KEY_6:"MJ", e.KEY_5:"MK", e.KEY_4:"ML", 
}

MACRO_RECORD = {
    e.KEY_F:"MA", e.KEY_E:"MB", e.KEY_D:"MC", e.KEY_C:"MD", e.KEY_B:"ME", e.KEY_A:"MF", 
    e.KEY_X:"MG", e.KEY_W:"MH", e.KEY_V:"MI", e.KEY_U:"MJ", e.KEY_T:"MK", e.KEY_S:"ML", 
}

MACRO_FINISH = {
    e.KEY_L:"MA", e.KEY_K:"MB", e.KEY_J:"MC", e.KEY_I:"MD", e.KEY_H:"ME", e.KEY_G:"MF", 
    e.KEY_3:"MG", e.KEY_2:"MH", e.KEY_1:"MI", e.KEY_0:"MJ", e.KEY_Z:"MK", e.KEY_Y:"ML", 
}


class VostroKBD_N(BaseConsumer):

    def __init__(self, core):
        super().__init__(core)

        self.vostro_map = {
            e.KEY_F10:e.KEY_PRINT, e.KEY_F11:e.KEY_HOME, e.KEY_F12:e.KEY_END,
            e.KEY_PRINT:e.KEY_F10, e.KEY_HOME:e.KEY_F11, e.KEY_END:e.KEY_F12, 
        }

        self.recording = {}
        self.recorded = {}

    def on_event(self, device_name, event):
        # info("Processing event", device_name)
        #import pdb; pdb.set_trace()

        if device_name == "AT Translated Set 2 keyboard":
            #info("Event from vostro keyboard")

            if event.type == e.EV_KEY:
                mapping = self.vostro_map.get(event.code)

                if mapping is not None:
                    event.code = mapping
        
        elif device_name == "Arduino LLC Arduino Leonardo":

            # We only handle EV_KEY events that are not release keys
            if event.type != e.EV_KEY or event.value == 0:
                return

            #info("Event from macro keyboard", e.EV[event.type], e.KEY[event.code], event.value)

            # This is a key to play a macro
            if event.code in MACRO_PLAY:
                macro_name = MACRO_PLAY[event.code]
                #info("Playing macro - ", macro_name)

                if macro_name in self.recorded:
                    sequence = self.recorded[macro_name]

                    for event in sequence:
                        self.core.out.forward(event)
                
                else:
                    warn("Attempting to execute a macro that does not exists - ", macro_name)
            
            # This is a key to start recording a macro
            elif event.code in MACRO_RECORD:
                macro_name = MACRO_RECORD[event.code]
                #info("Recording macro - ", macro_name)

                self.recording[macro_name] = []

            # This is a key to finish recording a macro
            elif event.code in MACRO_FINISH:
                macro_name = MACRO_FINISH[event.code]
                #info("Finishing macro - ", macro_name)

                if macro_name in self.recording:
                    self.recorded[macro_name] = self.recording[macro_name]
                    del self.recording[macro_name]

                else:
                    warn("Supposed to finish recording a macro that is not being recorded - ", macro_name)
            
            else:
                warn("Unmapped macro keyboard event - ", e.KEY[event.code])
            
            # We do not forward the key event, otherwise it may be recorded 
            # or received as input as text input by current the program.
            return
        
        else:
            # info("Event from a generic keyboard")
            pass
        
        
        # We register the key in any macro being recorded
        for macro_name, sequence in self.recording.items():
            info("Saving event to macro - ", macro_name)
            sequence.append(event)

        # Finally, we use our virtual device to input the processed event
        # info("forwarding event to virtual device")
        self.core.out.forward(event)


def on_init(core):

    core.consumers["VostroKBD_N"] = VostroKBD_N(core)
    core.set_consumer(TARGET_DEVICE, "VostroKBD_N")
