
from shadows.virtual_keyboard import VirtualKeyboardEvent, TOPIC_VIRTUALKEYBOARD_EVENT
from shadows.virtual_device import VirtualDeviceEvent
from shadows.virtual_pen import VirtualPenEvent

from threading import Thread, Lock
from evdev import ecodes as e
from reflex import Reflex

# from .libeye.eye import Eye, EyeException

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
            "group": "A",
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
                
                (e.KEY_L,1):[("save",)],
                (e.KEY_K,1):[("save",)],
                (e.KEY_J,1):[("save",)],
                (e.KEY_I,1):[("save",)],
                (e.KEY_H,1):[("save",)],
                (e.KEY_G,1):[("save",)],
                (e.KEY_3,1):[("save",)],
                (e.KEY_2,1):[("save",)],
                (e.KEY_1,1):[("save",)],
                (e.KEY_0,1):[("save",)],
                (e.KEY_Z,1):[("save",)],
                (e.KEY_Y,1):[("save",)],
            },
        },
    },

    "HyperX HyperX Mars Gaming KeyBoard": {
        "mem": {
            "state": "stateIdle",
            "group": "A",
        },

        "actions": {

            # State Idle. 
            # Macro keys will be executed a single time when pressed. 
            # Hold to repeat.

            "stateIdle": 
            {
                (e.KEY_NUMLOCK   ,1):[("move_group","A")], 
                (e.KEY_KPSLASH   ,1):[("move_group","B")], 
                (e.KEY_KPASTERISK,1):[("move_group","C")], 
                (e.KEY_KPMINUS   ,1):[("move_group","D")], 

                (e.KEY_KP0,1):[("play","0", 1)], 
                (e.KEY_KP1,1):[("play","1", 1)],
                (e.KEY_KP2,1):[("play","2", 1)],
                (e.KEY_KP3,1):[("play","3", 1)],
                (e.KEY_KP4,1):[("play","4", 1)],
                (e.KEY_KP5,1):[("play","5", 1)],
                (e.KEY_KP6,1):[("play","6", 1)], 
                (e.KEY_KP7,1):[("play","7", 1)],
                (e.KEY_KP8,1):[("play","8", 1)],
                (e.KEY_KP9,1):[("play","9", 1)],

                (e.KEY_KP0,2):[("play","0", 1)], 
                (e.KEY_KP1,2):[("play","1", 1)],
                (e.KEY_KP2,2):[("play","2", 1)],
                (e.KEY_KP3,2):[("play","3", 1)],
                (e.KEY_KP4,2):[("play","4", 1)],
                (e.KEY_KP5,2):[("play","5", 1)],
                (e.KEY_KP6,2):[("play","6", 1)], 
                (e.KEY_KP7,2):[("play","7", 1)],
                (e.KEY_KP8,2):[("play","8", 1)],
                (e.KEY_KP9,2):[("play","9", 1)],

                (e.KEY_KPENTER,1):[("interrupt",)],
                (e.KEY_KPDOT,1):[("interrupt",), ("move_state", "stateMore")],
            },

            # State More. 
            # Macro keys will be recorded when pressed.

            "stateMore": 
            {
                (e.KEY_KP0,1):[("record","0"), ("move_state","stateRec")], 
                (e.KEY_KP1,1):[("record","1"), ("move_state","stateRec")],
                (e.KEY_KP2,1):[("record","2"), ("move_state","stateRec")],
                (e.KEY_KP3,1):[("record","3"), ("move_state","stateRec")],
                (e.KEY_KP4,1):[("record","4"), ("move_state","stateRec")],
                (e.KEY_KP5,1):[("record","5"), ("move_state","stateRec")],
                (e.KEY_KP6,1):[("record","6"), ("move_state","stateRec")],
                (e.KEY_KP7,1):[("record","7"), ("move_state","stateRec")],
                (e.KEY_KP8,1):[("record","8"), ("move_state","stateRec")],
                (e.KEY_KP9,1):[("record","9"), ("move_state","stateRec")],

                (e.KEY_KPDOT,0):[("move_state", "stateIdle")],
            },

            # State Rec. 
            # Macro will be saved if DOT is pressed. 
            # Keys 0, 1, 2, and 3 will add delay (0.01, 0.1, 1, 10) seconds
            # Enter will cancel the recording

            "stateRec": {
                (e.KEY_KP0,1):[("wait",  0.01)], 
                (e.KEY_KP1,1):[("wait",  0.1)],
                (e.KEY_KP2,1):[("wait",  1)],
                (e.KEY_KP3,1):[("wait", 10)],

                (e.KEY_KPDOT,1):[("save",), ("move_state", "stateIdle")],
                (e.KEY_KPENTER,1):[("cancel",), ("move_state", "stateIdle")],
            },
        },
    },
}


class Macro:

    def __init__(self, name=None, importFrom=None):

        if importFrom is not None:
            # self.eye = Eye(base64data=importFrom["eye"])
            self.name = importFrom["name"]
            self.sequence = importFrom["sequence"]

        elif name is not None:
            # self.eye = Eye("./shadows/libeye/configs.json")
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
            # "eye": self.eye.exportAsBase64(),
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
    
    def play(self, macro:Macro, repeat):
        
        if not self.stop.locked():
            self.stop.acquire()

        try:

            for r in range(repeat):

                log.debug(f"Repeating play loop {r+1}/{repeat}, length {len(macro.sequence)}")

                for cmd in macro.sequence:

                    if not self.stop.locked():
                        self.stop.acquire()
                        return

                    cmd_type = cmd[0]
                    cmd_args = cmd[1:]

                    log.debug(f"  Playing cmd {cmd_type} with args {cmd_args}")

                    if cmd_type == "press_key":
                        if not self.play_press_key(macro, *cmd_args):
                            break

                    elif cmd_type == "wait":
                        if not self.play_wait(macro, *cmd_args):
                            break
                    
                    else:
                        log.debug("Invalid macro cmd: ", cmd_type)
                    
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
    
    # Called when a key from a macro keyboard is pressed
    def on_macro_event(self, device_name, event):

        if device_name.startswith("DeviceReader:"):
            device_name = device_name[13:]
        
        if not device_name in MACRO_KEYBOARDS:
            log.warn("Unmapped macro keyboard: ", device_name)
            return

        if event.type != e.EV_KEY:
            return
        
        group = MACRO_KEYBOARDS[device_name]["mem"]["group"]
        state = MACRO_KEYBOARDS[device_name]["mem"]["state"]
        actions = MACRO_KEYBOARDS[device_name]["actions"][state]
        action = (event.code, event.value)

        log.info(f"Processing a macro keyboard key:", e.keys[action[0]], action[1], state, group)

        if action in actions:

            for action in actions[action]:
                log.info(f"Parsing action: {action[0]}")

                try:

                    if action[0] == "move_state":
                        self.move_state(device_name, action[1])

                    elif action[0] == "move_group":
                        self.move_group(device_name, action[1])

                    elif action[0] == "play":
                        self.macro_play(device_name, action[1], action[2])

                    elif action[0] == "record":
                        self.macro_record_new(device_name, action[1])

                    elif action[0] == "save":
                        self.macro_save()

                    elif action[0] == "cancel":
                        self.macro_cancel()

                    elif action[0] == "interrupt":
                        log.info("Calling macro_interrupt")
                        self.macro_interrupt()

                    elif action[0] == "wait":
                        self.macro_push_delay(action[1])
                    
                    else:
                        log.error("Unknown action:", action)
                
                except Exception as err:
                    traceback.print_exc(file=sys.stdout)
                    log.error(err)


    def move_state(self, device_name, state_name):
        log.debug("Moving to state", state_name)
        MACRO_KEYBOARDS[device_name]["mem"]["state"] = state_name

    def move_group(self, device_name, group_name):
        log.debug("Moving to group", group_name)
        MACRO_KEYBOARDS[device_name]["mem"]["group"] = group_name

    def macro_interrupt(self):
        log.debug("Interrupting macro playback")
        self.macro_player.interrupt()
    
    def macro_push_delay(self, duration):
        if self.macro is not None:
            self.macro_player.push(("train_wait", self.macro, duration))

    def macro_play(self, device_name, macro_key, repeat):

        mem = MACRO_KEYBOARDS[device_name]["mem"]
        macro_name = mem["group"] + macro_key if "group" in mem else macro_key

        log.debug("Playing macro - ", macro_name)

        if macro_name in self.recorded:
            macro = self.recorded[macro_name]
            self.macro_player.push(("play", macro, repeat))

        else:
            log.warn("Attempting to execute a macro that does not exists - ", macro_name)

    def macro_record_new(self, device_name, macro_key):

        mem = MACRO_KEYBOARDS[device_name]["mem"]
        macro_name = mem["group"] + macro_key if "group" in mem else macro_key

        self.macro = Macro(macro_name)

        log.debug("Recording macro - ", macro_name)

    def macro_save(self):
        log.debug("Saving macro")

        if self.macro is None:
            log.error("Attempting to save a macro recording but no recording is in progress")
            return
        
        if len(self.macro.sequence) == 0:
            log.warn("Nothing to save, macro didn't capture any event - ", self.macro.name)
        else:
            self.recorded[self.macro.name] = self.macro
            self.export_macros()
        
        self.macro = None
    
    def macro_cancel(self):
        log.debug("Canceling macro recording")

        if self.macro is None:
            log.error("Attempting to cancel a macro recording but no recording is in progress")
            return
        
        self.macro = None

    # Called when a key is being sent to the virtual keyboard
    # This is used to record the macro
    def on_output_event(self, topic_name, event):

        # We ignore the event if no macro is being recorded
        if self.macro is None:
            return
        
        eventClass = event[0]

        if eventClass != VirtualDeviceEvent.FORWARD:
            return
        
        type   = event[1]
        code   = event[2]
        source = event[4] if len(event) >= 5 else None
        
        # We ignore keys generated from a macro playback
        if source in IGNORE_SOURCE:
            return
        
        # We also ignore SYN events
        if type in IGNORE_TYPE:
            return
        
        # And finally we ignore numpad keys
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
