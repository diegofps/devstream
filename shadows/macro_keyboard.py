from shadows.virtual_keyboard import TOPIC_DEVICEWRITER_EVENT, OutputEvent
from evdev import ecodes as e
from reflex import Reflex

import traceback
import pickle
import time
import sys
import log


MACRO_KEYBOARDS = [
    "Arduino LLC Arduino Leonardo", 
]


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


class MacroKeyboard(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)

        self.recording = {}
        self.recorded = {}

        self.import_macros()

        # Monitor output keys sent to virtual output device
        self.add_listener(TOPIC_DEVICEWRITER_EVENT, self.on_output_event)

        # Monitor macro keyboards keys
        for device_name in MACRO_KEYBOARDS:
            self.add_listener("DeviceReader:" + device_name, self.on_macro_event)

    def on_macro_event(self, device_name, event):
        # log.debug("Processing macro event from", device_name, event)
    
        # We only handle EV_KEY events that are not release keys
        if event.type != e.EV_KEY or event.value == 0:
            return

        # This is a key to play a macro
        if event.code in MACRO_PLAY:
            macro_name = MACRO_PLAY[event.code]
            log.debug("Playing macro - ", macro_name)

            if macro_name in self.recorded:
                sequence = self.recorded[macro_name]

                for event2 in sequence:
                    self.mind.emit(TOPIC_DEVICEWRITER_EVENT, event2)
                    
                # TODO: Required? 
                time.sleep(0.01)
            
            else:
                log.error("Attempting to execute a macro that does not exists - ", macro_name)
        
        # This is a key to start recording a macro
        elif event.code in MACRO_RECORD:
            macro_name = MACRO_RECORD[event.code]
            log.debug("Recording macro - ", macro_name)

            if macro_name in self.recording:
                print("Recording already in progress, inserting delay")
                eb = OutputEvent(self.mind)
                eb.sleep(0.1)
                self.recording[macro_name].append(eb.sequence[0])

            else:
                self.recording[macro_name] = []

        # This is a key to finish recording a macro
        elif event.code in MACRO_FINISH:
            macro_name = MACRO_FINISH[event.code]
            log.debug("Finishing macro - ", macro_name)

            if macro_name in self.recording:
                self.recorded[macro_name] = self.recording[macro_name]
                del self.recording[macro_name]
                self.export_macros()

            else:
                log.error("Supposed to finish recording a macro that is not being recorded - ", macro_name)
        
        else:
            log.error("Unmapped macro keyboard event - ", e.KEY[event.code])
        
    def on_output_event(self, topic_name, event):
        # log.info("Intercepting event", topic_name, event)

        # Keyboard events are always comming from Forward events
        # These are the ones we track
        if event[0] != OutputEvent.FORWARD:
            return
        
        # print(event)

        # We register the key in any macro being recorded
        for macro_name, sequence in self.recording.items():
            log.debug("Saving event to macro - ", macro_name)
            sequence.append(event)
    
    def export_macros(self):
        try:
            with open("./macros.bin", "wb") as fout:
                data = pickle.dumps(self.recorded)
                fout.write(data)
            log.info("Macros exported successfully")
        except:
            log.error("Could not export macros")
            traceback.print_exc(file=sys.stdout)

    def import_macros(self):
        try:
            with open("./macros.bin", "rb") as fin:
                self.recorded = pickle.loads(fin.read())
            log.info("Macros imported successfully")
        except:
            log.warn("Could not import macros, creating new buffers")
            traceback.print_exc(file=sys.stdout)
            self.recorded = {}
            self.export_macros()


def on_load(shadow):
    MacroKeyboard(shadow)
    shadow.require_device(MACRO_KEYBOARDS)
