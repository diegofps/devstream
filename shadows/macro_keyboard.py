from shadows.virtual_keyboard import TOPIC_DEVICEWRITER_EVENT, OutputEvent
from threading import Thread, Lock
from evdev import ecodes as e
from reflex import Reflex

from .libeye.eye import Eye, EyeException

import traceback
import pickle
import time
import sys
import log


SOURCE_NAME  = "MacroKeyboard"
FIND_TIMEOUT = 30.0


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
                (e.KEY_R,1):[("play","MA", 1)],
                (e.KEY_Q,1):[("play","MB", 1)],
                (e.KEY_P,1):[("play","MC", 1)],
                (e.KEY_O,1):[("play","MD", 1)],
                (e.KEY_N,1):[("play","ME", 1)],
                (e.KEY_M,1):[("play","MF", 1)],
                (e.KEY_9,1):[("play","MG", 1)],
                (e.KEY_8,1):[("play","MH", 1)],
                (e.KEY_7,1):[("play","MI", 1)],
                (e.KEY_6,1):[("play","MJ", 1)],
                (e.KEY_5,1):[("play","MK", 1)],
                (e.KEY_4,1):[("play","ML", 1)],

                (e.KEY_R,2):[("play","MA", 1)],
                (e.KEY_Q,2):[("play","MB", 1)],
                (e.KEY_P,2):[("play","MC", 1)],
                (e.KEY_O,2):[("play","MD", 1)],
                (e.KEY_N,2):[("play","ME", 1)],
                (e.KEY_M,2):[("play","MF", 1)],
                (e.KEY_9,2):[("play","MG", 1)],
                (e.KEY_8,2):[("play","MH", 1)],
                (e.KEY_7,2):[("play","MI", 1)],
                (e.KEY_6,2):[("play","MJ", 1)],
                (e.KEY_5,2):[("play","MK", 1)],
                (e.KEY_4,2):[("play","ML", 1)],

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

            # Default state. 
            # Macro keys will be executed a single time when pressed. 
            # Hold to repeat.

            "state1": {
                (e.KEY_KP0,1):[("play","KA", 1)], 
                (e.KEY_KP1,1):[("play","KB", 1)],
                (e.KEY_KP2,1):[("play","KC", 1)],
                (e.KEY_KP3,1):[("play","KD", 1)],
                (e.KEY_KP4,1):[("play","KE", 1)],
                (e.KEY_KP5,1):[("play","KF", 1)],
                (e.KEY_KP6,1):[("play","KG", 1)], 
                (e.KEY_KP7,1):[("play","KH", 1)],
                (e.KEY_KP8,1):[("play","KI", 1)],
                (e.KEY_KP9,1):[("play","KJ", 1)],

                (e.KEY_KP0,2):[("play","KA", 1)],
                (e.KEY_KP1,2):[("play","KB", 1)],
                (e.KEY_KP2,2):[("play","KC", 1)],
                (e.KEY_KP3,2):[("play","KD", 1)],
                (e.KEY_KP4,2):[("play","KE", 1)],
                (e.KEY_KP5,2):[("play","KF", 1)],
                (e.KEY_KP6,2):[("play","KG", 1)],
                (e.KEY_KP7,2):[("play","KH", 1)],
                (e.KEY_KP8,2):[("play","KI", 1)],
                (e.KEY_KP9,2):[("play","KJ", 1)],

                (e.KEY_KPDOT,1):[("move", "state2")],
            },

            # Record state. 
            # Macro keys will be recorded when pressed.
            # Hold to repeat.

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

            # Finish state. Macro will stop recording if DOT is pressed. 
            # Macro keys will be executed a single time if pressed.

            "state3": {
                (e.KEY_KP0,1):[("see",)],
                (e.KEY_KP1,1):[("see_and_click",   e.BTN_LEFT)],
                (e.KEY_KP2,1):[("see_and_click", e.BTN_MIDDLE)],
                (e.KEY_KP3,1):[("see_and_click",  e.BTN_RIGHT)],
                (e.KEY_KP4,1):[("see_and_drag",    e.BTN_LEFT)],
                (e.KEY_KP5,1):[("see_and_drag",  e.BTN_MIDDLE)],
                (e.KEY_KP6,1):[("see_and_drag",   e.BTN_RIGHT)],
                (e.KEY_KP7,1):[("wait", 0.1)],
                (e.KEY_KP8,1):[("wait", 1.0)],
                (e.KEY_KP9,1):[("wait", 10.0)],
                
                (e.KEY_KPDOT,1):[("finish",), ("move", "state1")],
            },
        },
    },
}


class MacroPlayer:

    def __init__(self, mind):

        self.mutex = Lock()
        self.ready = Lock()
        self.stop = Lock()

        self.done = False
        self.mind = mind

        self.ready.acquire()
        self.stop.acquire()

        self.thread = Thread(target=self.run)
        self.thread.start()

    def push(self, macro):
        self.mutex.acquire()

        try:
            if self.ready.locked:
                self.macro = macro
                self.ready.release()

        finally:
            self.mutex.release()

    def run(self):
        while not self.done:
            self.ready.acquire()

            if self.done:
                break

            macro, repeat = self.macro

            for _ in range(repeat):
                for type, bundle in macro.sequence:

                    if not self.stop.locked():
                        self.stop.acquire()
                        break

                    if type == "press_key":
                        if not self.press_key(macro, bundle):
                            break

                    elif type == "see":
                        if not self.see(macro, bundle):
                            break

                    elif type == "see_and_click":
                        if not self.see_and_click(macro, bundle):
                            break

                    elif type == "see_and_drag":
                        if not self.see_and_drag(macro, bundle):
                            break

                    elif type == "wait":
                        if not self.wait(macro, bundle):
                            break
                
                else:
                    # TODO: Required to pause between each playback?
                    # time.sleep(0.01)
                    continue
                break
            
            self.mutex.acquire()
            self.ready.release()
            self.mutex.release()
    
    def press_key(self, macro, bundle):
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, bundle)
        return True
    
    def see(self, macro, bundle):
        region1id = bundle[1]

        expires_at = time.time() + FIND_TIMEOUT
        target     = None

        while time.time() < expires_at:
            macro.eye.capture_screen()
            target = macro.eye.find(region1id)

            if not self.stop.locked():
                self.stop.acquire()
                return False

            if target is not None:
                return True

        return False

    def see_and_click(self, macro, bundle):
        # bundle: (region1, point1, region1id, button)

        region1      = bundle[0]
        point1       = bundle[1]
        region1id    = bundle[2]
        mouse_button = bundle[3]

        expires_at = time.time() + FIND_TIMEOUT
        target     = None

        while time.time() < expires_at:
            macro.eye.capture_screen()
            target = macro.eye.find(region1id)

            if not self.stop.locked():
                self.stop.acquire()
                return False

            if target is not None:
                break

        if target is None:
            return False

        x = target[0] + point1[0] - region1[0]
        y = target[1] + point1[1] - region1[1]

        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_ABS, e.ABS_X, x, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_ABS, e.ABS_Y, y, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, SOURCE_NAME))

        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_KEY, mouse_button, 1, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_KEY, mouse_button, 0, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, SOURCE_NAME))

        return True

    def see_and_drag(self, macro, bundle):
        # bundle: (region1, region2, point1, point2, region1id, region2id, button)
        
        # Unwrap bundle

        region1      = bundle[0]
        region2      = bundle[1]
        point1       = bundle[2]
        point2       = bundle[3]
        region1id    = bundle[4]
        region2id    = bundle[5]
        mouse_button = bundle[6]

        # Look for first region

        expire1 = time.time() + FIND_TIMEOUT
        target1 = None

        while time.time() < expire1:
            macro.eye.capture_screen()
            target = macro.eye.find(region1id)

            if not self.stop.locked():
                self.stop.acquire()
                return False

            if target is not None:
                break

        if target is None:
            return False

        # Look for second region

        expire2 = time.time() + FIND_TIMEOUT
        target2 = None

        while time.time() < expire2:
            macro.eye.capture_screen()
            target2 = macro.eye.find(region2id)

            if not self.stop.locked():
                self.stop.acquire()
                return False

            if target2 is not None:
                break

        if target2 is None:
            return False

        # Coordinates of the click and drag points

        x1 = target1[0] + point1[0] - region1[0]
        y1 = target1[1] + point1[1] - region1[1]

        x2 = target2[0] + point2[0] - region2[0]
        y2 = target2[1] + point2[1] - region2[1]

        # Move to first coordinate

        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_ABS, e.ABS_X, x1, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_ABS, e.ABS_Y, y1, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, SOURCE_NAME))
        time.sleep(0.1);

        # Simulate click

        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_KEY, mouse_button, 1, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, SOURCE_NAME))
        time.sleep(0.1);

        # Move to second coordinate

        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_ABS, e.ABS_X, x2, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_ABS, e.ABS_Y, y2, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, SOURCE_NAME))
        time.sleep(0.1);

        # Simulate click release

        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_KEY, mouse_button, 0, SOURCE_NAME))
        self.mind.emit(TOPIC_DEVICEWRITER_EVENT, (OutputEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, SOURCE_NAME))
        time.sleep(0.1);

        return True

    def wait(self, macro, bundle):
        seconds = bundle[0]

        if seconds < 1.0:
            time.sleep(seconds)
            return True
        
        else:
            expire = time.time() + seconds

            while time.time() < expire:
                if not self.stop.locked():
                    self.stop.acquire()
                    return False

                time.sleep(0.1)

            return True

    def interrupt(self):
        if self.ready.locked():
            self.stop.release()

    def terminate(self):
        self.done = True
        self.ready.release()


class Macro:

    def __init__(self, name=None, importFrom=None):

        if importFrom is not None:
            self.eye = Eye(base64data=importFrom["eye"])
            self.name = importFrom["name"]
            self.sequence = importFrom["sequence"]

        elif name is not None:
            self.eye = Eye("./configs.json")
            self.sequence = []
            self.name = name
        
        else:
            raise Exception("Invalid arguments")
    
    @staticmethod
    def importFromDict(self, data):
        return Macro(importFrom=data)
    
    def exportAsDict(self):
        return {
            "name": self.name,
            "eye": self.eye.exportAsBase64(),
            "sequence": self.sequence,
        }


class MacroKeyboard(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)

        self.macro_player = MacroPlayer(self.mind)
        self.recorded = {}
        self.macro = None

        self.import_macros()

        # Monitor output keys sent to virtual output device

        self.add_listener(TOPIC_DEVICEWRITER_EVENT, self.on_output_event)

        # Monitor macro keyboards keys

        for device_name in MACRO_KEYBOARDS.keys():
            self.add_listener("DeviceReader:" + device_name, self.on_macro_event)

    def on_remove(self):
        super().on_remove()
        self.macro_player.terminate()
    
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
                    self.play(action[1], action[2])

                elif action[0] == "record":
                    self.record_macro(action[1])

                elif action[0] == "finish":
                    self.finish_macro()

                elif action[0] == "interrupt":
                    self.interrupt_macro()

                elif action[0] == "see":
                    self.see()

                elif action[0] == "see_and_click":
                    self.see_and_click(action[1])
                
                elif action[0] == "see_and_drag":
                    self.see_and_drag(action[1])
                
                elif action[0] == "wait":
                    self.wait(action[1])
                
                else:
                    log.error("Unknown action - ", action)

    def see(self):
        if self.macro is None:
            return
        
        try:
            self.macro.eye.capture_screen()
            region1   = self.macro.eye.request_region("Select the reference region to search for")
            region1id = self.macro.eye.learn(region1)
            bundle    = (region1, region1id)
            self.macro.append(("see", bundle))

        except EyeException as e:
            log.info("Interrupted see - ", e)

    def see_and_click(self, button):
        if self.macro is None:
            return
        
        try:
            self.macro.eye.capture_screen()
            region1   = self.macro.eye.request_region("Select the reference region to search for")
            point1    = self.macro.eye.request_point("Select coordinate to click")
            region1id = self.macro.eye.learn(region1)
            bundle    = (region1, point1, region1id, button)
            self.macro.append(("see_and_click", bundle))

        except EyeException as e:
            log.info("Interrupted see_and_click - ", e)

    def see_and_drag(self, button):
        if self.macro is None:
            return
        
        try:
            self.macro.eye.capture_screen()

            region1 = self.macro.eye.request_region("Select the first reference region to search for")
            point1  = self.macro.eye.request_point("Select coordinate to click")

            region2 = self.macro.eye.request_region("Select the second reference region to search for")
            point2  = self.macro.eye.request_point("Select coordinate to release the click")

            region1id = self.macro.eye.learn(region1)
            region2id = self.macro.eye.learn(region2)

            bundle = (region1, region2, point1, point2, region1id, region2id, button)

            self.macro.append(("see_and_drag", bundle))

        except EyeException as e:
            log.info("Interrupted see_and_drag - ", e)

    def wait(self, duration):
        if self.macro is not None:
            bundle = (duration,)
            self.macro.append(("wait", bundle))

    def interrupt_macro(self):
        log.debug("Interrupting macro")

        self.macro_player.interrupt()
    
    def play(self, macro_name, repeat):
        log.debug("Playing macro - ", macro_name)

        if macro_name in self.recorded:
            macro = self.recorded[macro_name]
            self.macro_player.push((macro, repeat))

        else:
            log.error("Attempting to execute a macro that does not exists - ", macro_name)

    def record_macro(self, macro_name):
        log.debug("Recording macro - ", macro_name)

        self.macro = Macro(macro_name)

    def finish_macro(self):
        log.debug("Finishing macro recording")

        if self.macro is None:
            log.error("Attempting to finish a macro recording but no recording is in progress")
            return
        
        if len(self.macro.sequence) == 0:
            log.error("Nothing to save, macro didn't capture any event - ", self.macro.name)
        else:
            self.recorded[self.macro.name] = self.macro
            self.export_macros()
        
        self.macro = None
    
    def on_output_event(self, topic_name, event):

        # Check if we should ignore this event

        if self.macro is None:
            return
        
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

        # Register the key in the macro's sequence

        log.debug(f"Saving event to macro '", self.macro.name, "', '", event, "'")

        task = ("press_key", event)
        self.macro.sequence.append(task)

        task = ("press_key", (OutputEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, source))
        self.macro.sequence.append(task)
    
    def export_macros(self):
        try:
            data = { k:v.exportAsDict() for k,v in self.recorded.items() }
            data = pickle.dumps(data)

            with open("./macros.bin", "wb") as fout:
                fout.write(data)

            log.info("Macros exported successfully")
        except:
            log.error("Could not export macros")
            traceback.print_exc(file=sys.stdout)

    def import_macros(self):
        try:
            with open("./macros.bin", "rb") as fin:
                data = fin.read()
                data = { k:Macro.importFrom(v) for k,v in data.items() }
                self.recorded = pickle.loads(data)
            log.info("Macros imported successfully")
        except:
            log.error("Could not import macros, creating new buffer")
            traceback.print_exc(file=sys.stdout)
            self.recorded = {}
            # self.export_macros()


def on_load(shadow):
    MacroKeyboard(shadow)
    shadow.require_device(list(MACRO_KEYBOARDS.keys()))
