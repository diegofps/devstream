from shadows.virtual_keyboard import TOPIC_DEVICEWRITER_EVENT, OutputEvent
from evdev import ecodes as e
from reflex import Reflex

import traceback
import pickle
import time
import sys
import log


IGNORE_SOURCE = set([
    "MacroKeyboard:RecordedEvent"
])

IGNORE_TYPE = set([
    e.EV_SYN, e.EV_MSC
])

IGNORE_CODE = set([
    e.KEY_KP0, e.KEY_KP1, e.KEY_KP2, e.KEY_KP3, e.KEY_KP4, e.KEY_KP5, e.KEY_KP6, e.KEY_KP7, e.KEY_KP8, e.KEY_KP9, e.KEY_KPDOT
])

IGNORE_SOURCE_AND_CODE = {
    "DeviceReader:CORSAIR CORSAIR K63 Wireless Mechanical Gaming Keyboard": set([
        e.KEY_KP0, e.KEY_KP1, e.KEY_KP2, e.KEY_KP3, e.KEY_KP4, e.KEY_KP5, e.KEY_KP6, e.KEY_KP7, e.KEY_KP8, e.KEY_KP9, e.KEY_KPDOT
    ]),
}

IGNORE_SOURCE_AND_TYPE = {
    "DeviceReader:CORSAIR CORSAIR K63 Wireless Mechanical Gaming Keyboard": set([
        e.EV_SYN, e.EV_MSC
    ]),
}


MACRO_KEYBOARDS = {
    "Arduino LLC Arduino Leonardo": {
        "mem": {
            "state": "state1",
        },
        
        "actions": {
            "state1": {
                (e.KEY_R,1):[("play","MA")],
                (e.KEY_Q,1):[("play","MB")],
                (e.KEY_P,1):[("play","MC")],
                (e.KEY_O,1):[("play","MD")],
                (e.KEY_N,1):[("play","ME")],
                (e.KEY_M,1):[("play","MF")],
                (e.KEY_9,1):[("play","MG")],
                (e.KEY_8,1):[("play","MH")],
                (e.KEY_7,1):[("play","MI")],
                (e.KEY_6,1):[("play","MJ")],
                (e.KEY_5,1):[("play","MK")],
                (e.KEY_4,1):[("play","ML")],

                (e.KEY_R,2):[("play","MA")],
                (e.KEY_Q,2):[("play","MB")],
                (e.KEY_P,2):[("play","MC")],
                (e.KEY_O,2):[("play","MD")],
                (e.KEY_N,2):[("play","ME")],
                (e.KEY_M,2):[("play","MF")],
                (e.KEY_9,2):[("play","MG")],
                (e.KEY_8,2):[("play","MH")],
                (e.KEY_7,2):[("play","MI")],
                (e.KEY_6,2):[("play","MJ")],
                (e.KEY_5,2):[("play","MK")],
                (e.KEY_4,2):[("play","ML")],

                (e.KEY_F,1):[("record","MA")],
                (e.KEY_E,1):[("record","MB")],
                (e.KEY_D,1):[("record","MC")],
                (e.KEY_C,1):[("record","MD")],
                (e.KEY_B,1):[("record","ME")],
                (e.KEY_A,1):[("record","MF")],
                (e.KEY_X,1):[("record","MG")],
                (e.KEY_W,1):[("record","MH")],
                (e.KEY_V,1):[("record","MI")],
                (e.KEY_U,1):[("record","MJ")],
                (e.KEY_T,1):[("record","MK")],
                (e.KEY_S,1):[("record","ML")],
                
                (e.KEY_L,1):[("finish",)],
                (e.KEY_K,1):[("finish",)],
                (e.KEY_J,1):[("finish",)],
                (e.KEY_I,1):[("finish",)],
                (e.KEY_H,1):[("finish",)],
                (e.KEY_G,1):[("finish",)],
                (e.KEY_3,1):[("finish",)],
                (e.KEY_2,1):[("finish",)],
                (e.KEY_1,1):[("finish",)],
                (e.KEY_0,1):[("finish",)],
                (e.KEY_Z,1):[("finish",)],
                (e.KEY_Y,1):[("finish",)],
            },
        },
    },

    "HyperX HyperX Mars Gaming KeyBoard": {
        "mem": {
            "state": "state1",
        },

        "actions": {
            "state1": {
                (e.KEY_KP0,1):[("play","KA")], 
                (e.KEY_KP1,1):[("play","KB")],
                (e.KEY_KP2,1):[("play","KC")],
                (e.KEY_KP3,1):[("play","KD")],
                (e.KEY_KP4,1):[("play","KE")],
                (e.KEY_KP5,1):[("play","KF")],
                (e.KEY_KP6,1):[("play","KG")], 
                (e.KEY_KP7,1):[("play","KH")],
                (e.KEY_KP8,1):[("play","KI")],
                (e.KEY_KP9,1):[("play","KJ")],

                (e.KEY_KP0,2):[("play","KA")],
                (e.KEY_KP1,2):[("play","KB")],
                (e.KEY_KP2,2):[("play","KC")],
                (e.KEY_KP3,2):[("play","KD")],
                (e.KEY_KP4,2):[("play","KE")],
                (e.KEY_KP5,2):[("play","KF")],
                (e.KEY_KP6,2):[("play","KG")],
                (e.KEY_KP7,2):[("play","KH")],
                (e.KEY_KP8,2):[("play","KI")],
                (e.KEY_KP9,2):[("play","KJ")],
                
                (e.KEY_KPDOT,1):[("move", "state2")],
            },

            "state2": {
                (e.KEY_KP0,1):[("record","KA"), ("move","state3")], 
                (e.KEY_KP1,1):[("record","KB"), ("move","state3")],
                (e.KEY_KP2,1):[("record","KC"), ("move","state3")],
                (e.KEY_KP3,1):[("record","KD"), ("move","state3")],
                (e.KEY_KP4,1):[("record","KE"), ("move","state3")],
                (e.KEY_KP5,1):[("record","KF"), ("move","state3")],
                (e.KEY_KP6,1):[("record","KG"), ("move","state3")],
                (e.KEY_KP7,1):[("record","KH"), ("move","state3")],
                (e.KEY_KP8,1):[("record","KI"), ("move","state3")],
                (e.KEY_KP9,1):[("record","KJ"), ("move","state3")],

                (e.KEY_KPDOT,0):[("move", "state1")],
            },

            "state3": {
                (e.KEY_KP0,1):[("play","KA")],
                (e.KEY_KP1,1):[("play","KB")],
                (e.KEY_KP2,1):[("play","KC")],
                (e.KEY_KP3,1):[("play","KD")],
                (e.KEY_KP4,1):[("play","KE")],
                (e.KEY_KP5,1):[("play","KF")],
                (e.KEY_KP6,1):[("play","KG")],
                (e.KEY_KP7,1):[("play","KH")],
                (e.KEY_KP8,1):[("play","KI")],
                (e.KEY_KP9,1):[("play","KJ")],

                (e.KEY_KP0,2):[("play","KA")],
                (e.KEY_KP1,2):[("play","KB")],
                (e.KEY_KP2,2):[("play","KC")],
                (e.KEY_KP3,2):[("play","KD")],
                (e.KEY_KP4,2):[("play","KE")],
                (e.KEY_KP5,2):[("play","KF")],
                (e.KEY_KP6,2):[("play","KG")],
                (e.KEY_KP7,2):[("play","KH")],
                (e.KEY_KP8,2):[("play","KI")],
                (e.KEY_KP9,2):[("play","KJ")],

                (e.KEY_KPDOT,1):[("finish",), ("move", "state1")],
            },
        },
    },
}


class MacroKeyboard(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)

        self.recording_name = None
        self.recording = []
        self.recorded = {}

        self.import_macros()

        # Monitor output keys sent to virtual output device

        self.add_listener(TOPIC_DEVICEWRITER_EVENT, self.on_output_event)

        # Monitor macro keyboards keys

        for device_name in MACRO_KEYBOARDS.keys():
            self.add_listener("DeviceReader:" + device_name, self.on_macro_event)

    def on_macro_event(self, device_name, event):

        if device_name.startswith("DeviceReader:"):
            device_name = device_name[13:]
        
        if not device_name in MACRO_KEYBOARDS:
            log.warn("Unmapped macro keyboard - ", device_name)
            return

        if event.type != e.EV_KEY:
            return
        
        state = MACRO_KEYBOARDS[device_name]["mem"]["state"]
        actions = MACRO_KEYBOARDS[device_name]["actions"][state]

        action = (event.code, event.value)

        if action in actions:
            for action in actions[action]:
                if action[0] == "move":
                    MACRO_KEYBOARDS[device_name]["mem"]["state"] = action[1]
                elif action[0] == "play":
                    self.play_macro(action[1])
                elif action[0] == "record":
                    self.record_macro(action[1])
                elif action[0] == "finish":
                    self.finish_macro()
                else:
                    log.error("Unknown action - ", action)

    def play_macro(self, macro_name):
        log.debug("Playing macro - ", macro_name)

        if macro_name in self.recorded:
            sequence = self.recorded[macro_name]

            for event2 in sequence:
                self.mind.emit(TOPIC_DEVICEWRITER_EVENT, event2)

            # TODO: Required?

            time.sleep(0.01)

        else:
            log.error("Attempting to execute a macro that does not exists - ", macro_name)

    def record_macro(self, macro_name):
        log.debug("Recording macro - ", macro_name)

        self.recording_name = macro_name
        self.recording = []

    def finish_macro(self):
        log.debug("Finishing macro recording")

        if self.recording_name is None:
            log.error("Attempting to finish a macro recording that was not started")
            return
        
        if len(self.recording) == 0:
            log.error("Nothing to save, macro didn't register any event - ", self.recording_name)
        else:
            self.recorded[self.recording_name] = self.recording
            self.export_macros()
        
        self.recording_name = None
    
    def on_output_event(self, topic_name, event):

        # Check if we should ignore this event

        eventClass = event[0]

        if eventClass != OutputEvent.FORWARD:
            return
        
        type   = event[1]
        code   = event[2]
        source = event[4] if len(event) >= 5 else None
        
        if source in IGNORE_SOURCE:
            return
        
        if type in IGNORE_TYPE:
            return
        
        if code in IGNORE_CODE:
            return
        
        if source in IGNORE_SOURCE_AND_CODE and code in IGNORE_SOURCE_AND_CODE[source]:
            return

        # Register the key in the recording list

        if self.recording_name is not None:
            log.debug(f"Saving event to macro '", self.recording_name, "', '", event, "'")
            self.recording.append(event)
            self.recording.append((OutputEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, source))
    
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
    shadow.require_device(list(MACRO_KEYBOARDS.keys()))
