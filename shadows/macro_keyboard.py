
from shadows.virtual_keyboard import VirtualKeyboardEvent, TOPIC_VIRTUALKEYBOARD_EVENT
from shadows.virtual_device import VirtualDeviceEvent
from shadows.virtual_pen import VirtualPenEvent

from threading import Thread, Lock
from evdev import ecodes as e
from reflex import Reflex

from .libeye.eye import Eye, EyeException

import traceback
import pickle
import time
import sys
import log


SOURCE_MACRO_KEYBOARD  = "Macro Keyboard"
FIND_TIMEOUT = 30.0


IGNORE_SOURCE = set([
    "Macro Keyboard"
])

IGNORE_TYPE = set([
    e.EV_SYN, e.EV_MSC
])

IGNORE_CODE = set([
    e.KEY_KP0, e.KEY_KP1, e.KEY_KP2, e.KEY_KP3, e.KEY_KP4, e.KEY_KP5, e.KEY_KP6, e.KEY_KP7, e.KEY_KP8, e.KEY_KP9, e.KEY_KPDOT
])

# IGNORE_SOURCE_AND_CODE = {
#     "DeviceReader:CORSAIR CORSAIR K63 Wireless Mechanical Gaming Keyboard": set([
#         e.KEY_KP0, e.KEY_KP1, e.KEY_KP2, e.KEY_KP3, e.KEY_KP4, e.KEY_KP5, e.KEY_KP6, e.KEY_KP7, e.KEY_KP8, e.KEY_KP9, e.KEY_KPDOT
#     ]),
# }

# IGNORE_SOURCE_AND_TYPE = {
#     "DeviceReader:CORSAIR CORSAIR K63 Wireless Mechanical Gaming Keyboard": set([
#         e.EV_SYN, e.EV_MSC
#     ]),
# }


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

                (e.KEY_KPDOT,1):[("interrupt"), ("move", "state2")],
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


class Macro:

    def __init__(self, name=None, importFrom=None):

        if importFrom is not None:
            self.eye = Eye(base64data=importFrom["eye"])
            self.name = importFrom["name"]
            self.sequence = importFrom["sequence"]

        elif name is not None:
            self.eye = Eye("./shadows/libeye/configs.json")
            self.sequence = []
            self.name = name
        
        else:
            raise Exception("Invalid arguments")
    
    @staticmethod
    def importFromDict(data):
        return Macro(importFrom=data)
    
    def exportAsDict(self):
        return {
            "name": self.name,
            "eye": self.eye.exportAsBase64(),
            "sequence": self.sequence,
        }


class MacroPlayer:

    def __init__(self, mind):

        self.done = False
        self.mind = mind
        self.task = None

        self.producer = Lock()
        self.consumer = Lock()
        self.stop     = Lock()

        self.consumer.acquire()
        self.stop.acquire()

        self.thread = Thread(target=self.run)
        self.thread.start()

    def push(self, task):
        if self.producer.acquire(blocking=False):
            self.task = task
            self.consumer.release()

    def run(self):

        while not self.done:
            self.consumer.acquire()

            try:
                if self.done:
                    break

                task_type = self.task[0]
                task_args = self.task[1:]

                log.debug("MacroPlayer: task: ", task_type, task_args)

                if task_type == "play":
                    self.play(*task_args)

                elif task_type == "train_see":
                    self.train_see(*task_args)

                elif task_type == "train_see_and_click":
                    self.train_see_and_click(*task_args)

                elif task_type == "train_see_and_drag":
                    self.train_see_and_drag(*task_args)
                
                elif task_type == "train_wait":
                    self.train_wait(*task_args)

                elif task_type == "train_press_key":
                    self.train_press_key(*task_args)
                
                else:
                    log.debug("Invalid task type: ", task_type)
            
            except:
                traceback.print_exc()
                log.error("MacroPlayer: task failed: ", task_type, task_args)

            self.producer.release()
    
    def train_press_key(self, macro:Macro, event1, event2):

        cmd = ("press_key", event1)
        macro.sequence.append(cmd)

        cmd = ("press_key", event2)
        macro.sequence.append(cmd)

        log.debug("train_press_key finished successfully")

    def train_wait(self, macro:Macro, duration):
        
        cmd = ("wait", duration)
        macro.sequence.append(cmd)
    
    def train_see(self, macro:Macro):

        try:
            macro.eye.capture_screen()

            region1   = macro.eye.request_region("Select the reference region to search for")
            region1id = macro.eye.learn(region1)

            cmd       = ("see", region1, region1id)

            macro.sequence.append(cmd)

        except EyeException as e:
            log.info("Interrupted see - ", e)
    
    def train_see_and_click(self, macro:Macro, button):

        try:
            macro.eye.capture_screen()

            region1   = macro.eye.request_region("Select the reference region to search for")
            point1    = macro.eye.request_point("Select coordinate to click")
            region1id = macro.eye.learn(region1)

            cmd       = ("see_and_click", region1, point1, region1id, button)
            
            macro.sequence.append(cmd)

        except EyeException as e:
            log.info("Interrupted see_and_click - ", e)
    
    def train_see_and_drag(self, macro:Macro, button):
        
        try:
            macro.eye.capture_screen()

            region1   = macro.eye.request_region("Select the first reference region to search for")
            point1    = macro.eye.request_point("Select coordinate to click")

            region2   = macro.eye.request_region("Select the second reference region to search for")
            point2    = macro.eye.request_point("Select coordinate to release the click")

            region1id = macro.eye.learn(region1)
            region2id = macro.eye.learn(region2)

            cmd       = ("see_and_drag", region1, region2, point1, point2, region1id, region2id, button)

            macro.sequence.append(cmd)

        except EyeException as e:
            log.info("Interrupted see_and_drag - ", e)

    def play(self, macro:Macro, repeat):
        
        try:

            for r in range(repeat):

                log.debug(f"Repeating play loop {r+1}/{repeat}")

                for cmd in macro.sequence:

                    if not self.stop.locked():
                        self.stop.acquire()
                        break

                    cmd_type = cmd[0]
                    cmd_args = cmd[1:]

                    log.debug(f"  Playing cmd {cmd_type} with args {cmd_args}")

                    if cmd_type == "press_key":
                        if not self.play_press_key(macro, *cmd_args):
                            break

                    elif cmd_type == "see":
                        if not self.play_see(macro, *cmd_args):
                            break

                    elif cmd_type == "see_and_click":
                        if not self.play_see_and_click(macro, *cmd_args):
                            break

                    elif cmd_type == "see_and_drag":
                        if not self.play_see_and_drag(macro, *cmd_args):
                            break

                    elif cmd_type == "wait":
                        if not self.play_wait(macro, *cmd_args):
                            break
                    
                    else:
                        log.debug("Invalid cmd type: ", cmd_type)
                    
                else:
                    # TODO: Required to pause between each playback?
                    # time.sleep(0.01)
                    continue
                break
        
        except:
            traceback.print_exc()
            log.error("MacroPlayer: cmd failed: ", cmd_type, cmd_args)

    def play_press_key(self, macro:Macro, event):
        
        log.debug("Sending event to DeviceWriter:", event)
        
        with VirtualKeyboardEvent(self.mind, SOURCE_MACRO_KEYBOARD) as eb:
            eb.forward(event[1], event[2], event[3])
        # self.mind.emit(TOPIC_VIRTUALKEYBOARD_EVENT, event)

        return True
    
    def play_see(self, macro:Macro, region1, region1id):

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

    def play_see_and_click(self, macro:Macro, region1, point1, region1id, mouse_button):
        
        expires_at = time.time() + FIND_TIMEOUT
        target     = None

        log.debug(1)
        macro.eye.capture_screen()
        log.debug(2)

        while time.time() < expires_at:
            target = macro.eye.find(region1id)
            log.debug(3)

            if not self.stop.locked():
                self.stop.acquire()
                return False

            log.debug(4)

            if target is not None:
                log.debug("Target found:", target)
                break

            log.debug(5)
            macro.eye.capture_screen()
            log.debug(6)

        log.debug(7)
        if target is None:
            log.debug("Target not found, returning")
            return False

        log.debug(8)
        screen_width, screen_height = macro.eye.screen_size()
        log.debug(9)

        x = int((target[0] + point1[0] - region1[0]) * 32767 / screen_width)
        y = int((target[1] + point1[1] - region1[1]) * 32767 / screen_height)

        log.debug("Click coordinates:", x, y)
        log.debug("  x ref:", target[0], point1[0], region1[0])
        log.debug("  y ref:", target[1], point1[1], region1[1])

        with VirtualPenEvent(self.mind, SOURCE_MACRO_KEYBOARD) as eb:

            # Move the mouse to the desired position

            eb.forward(e.EV_ABS, e.ABS_X, x)
            eb.forward(e.EV_ABS, e.ABS_Y, y)
            eb.forward(e.EV_SYN, e.SYN_REPORT, 0)
            eb.sleep(0.25)

            # Click the mouse

            eb.forward(e.EV_KEY, mouse_button, 1)
            eb.forward(e.EV_SYN, e.SYN_REPORT, 0)
            eb.sleep(0.1)

            # Release the mouse

            eb.forward(e.EV_KEY, mouse_button, 0)
            eb.forward(e.EV_SYN, e.SYN_REPORT, 0)
            eb.sleep(0.1)

        log.debug("play_see_and_click finished")

        return True

    def play_see_and_drag(self, macro:Macro, region1, region2, point1, point2, region1id, region2id, mouse_button):
        
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

        with VirtualPenEvent(self.mind, SOURCE_MACRO_KEYBOARD) as eb:

            # Move to first coordinate

            eb.forward(e.EV_ABS, e.ABS_X, x1)
            eb.forward(e.EV_ABS, e.ABS_Y, y1)
            eb.forward(e.EV_SYN, e.SYN_REPORT, 0)
            eb.sleep(0.25)

            # Simulate click

            eb.forward(e.EV_KEY, mouse_button, 1)
            eb.forward(e.EV_SYN, e.SYN_REPORT, 0)
            eb.sleep(0.1)

            # Move to second coordinate

            eb.forward(e.EV_ABS, e.ABS_X, x2)
            eb.forward(e.EV_ABS, e.ABS_Y, y2)
            eb.forward(e.EV_SYN, e.SYN_REPORT, 0)
            eb.sleep(0.1)

            # Simulate click release

            eb.forward(e.EV_KEY, mouse_button, 0)
            eb.forward(e.EV_SYN, e.SYN_REPORT, 0)
            eb.sleep(0.1)

        return True

    def play_wait(self, macro:Macro, seconds):
        
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
        if self.consumer.locked():
            self.stop.release()

    def terminate(self):
        self.done = True
        self.consumer.release()


class MacroKeyboard(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)

        self.macro_player = MacroPlayer(self.mind)
        self.recorded = {}
        self.macro = None

        self.import_macros()

        # Monitor output keys sent to virtual output device

        self.add_listener(TOPIC_VIRTUALKEYBOARD_EVENT, self.on_output_event)

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

    def interrupt_macro(self):
        log.debug("Interrupting macro")

        self.macro_player.interrupt()
    
    def see(self):
        if self.macro is not None:
            self.macro_player.push(("train_see", self.macro))

    def see_and_click(self, button):
        if self.macro is not None:
            self.macro_player.push(("train_see_and_click", self.macro, button))

    def see_and_drag(self, button):
        if self.macro is not None:
            self.macro_player.push(("train_see_and_click", self.macro, button))
    
    def wait(self, duration):
        if self.macro is not None:
            self.macro_player.push(("train_wait", self.macro, duration))

    def play(self, macro_name, repeat):
        log.debug("Playing macro - ", macro_name)

        if macro_name in self.recorded:
            macro = self.recorded[macro_name]
            self.macro_player.push(("play", macro, repeat))

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

        if eventClass != VirtualDeviceEvent.FORWARD:
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
        
        # if source in IGNORE_SOURCE_AND_CODE and code in IGNORE_SOURCE_AND_CODE[source]:
        #     return

        # Register the key in the macro's sequence

        log.debug(f"Saving event to macro '", self.macro.name, "', '", event, "'")

        event2 = (VirtualDeviceEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, source)
        self.macro_player.push(("train_press_key", self.macro, event, event2))
    
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
                data = pickle.loads(data)
                self.recorded = { k:Macro.importFromDict(v) for k,v in data.items() }
            log.info("Macros imported successfully")
        except:
            log.error("Could not import macros, creating new buffer")
            traceback.print_exc(file=sys.stdout)
            self.recorded = {}
            # self.export_macros()


def on_load(shadow):
    MacroKeyboard(shadow)
    shadow.require_device(list(MACRO_KEYBOARDS.keys()))
