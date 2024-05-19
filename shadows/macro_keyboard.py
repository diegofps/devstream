
from shadows.virtual_keyboard import VirtualKeyboardEvent, TOPIC_VIRTUALKEYBOARD_EVENT
from shadows.xppen_deco_pro import TOPIC_NOTIFICATION_STRONG, TOPIC_NOTIFICATION_WEAK
from shadows.virtual_device import VirtualDeviceEvent
from shadows.watch_login import TOPIC_LOGIN_CHANGED
from shadows.virtual_pen import VirtualPenEvent

from threading import Thread, Lock
from evdev import ecodes as e
from reflex import Reflex

# from .libeye.eye import Eye, EyeException

import subprocess
import traceback
import threading
import pickle
import time
import sys
import log
import os

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

                (e.KEY_F,1):[("record","MA"), ("notify", "Recording", "MA", 1)],
                (e.KEY_E,1):[("record","MB"), ("notify", "Recording", "MB", 1)],
                (e.KEY_D,1):[("record","MC"), ("notify", "Recording", "MC", 1)],
                (e.KEY_C,1):[("record","MD"), ("notify", "Recording", "MD", 1)],
                (e.KEY_B,1):[("record","ME"), ("notify", "Recording", "ME", 1)],
                (e.KEY_A,1):[("record","MF"), ("notify", "Recording", "MF", 1)],
                (e.KEY_X,1):[("record","MG"), ("notify", "Recording", "MG", 1)],
                (e.KEY_W,1):[("record","MH"), ("notify", "Recording", "MH", 1)],
                (e.KEY_V,1):[("record","MI"), ("notify", "Recording", "MI", 1)],
                (e.KEY_U,1):[("record","MJ"), ("notify", "Recording", "MJ", 1)],
                (e.KEY_T,1):[("record","MK"), ("notify", "Recording", "MK", 1)],
                (e.KEY_S,1):[("record","ML"), ("notify", "Recording", "ML", 1)],
                
                (e.KEY_L,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_K,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_J,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_I,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_H,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_G,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_3,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_2,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_1,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_0,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_Z,1):[("save",), ("notify", "Recording", "", 0)],
                (e.KEY_Y,1):[("save",), ("notify", "Recording", "", 0)],
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
                (e.KEY_NUMLOCK   ,1):[("move_group","A"), ("weak_notify","Group","A")], 
                (e.KEY_KPSLASH   ,1):[("move_group","B"), ("weak_notify","Group","B")], 
                (e.KEY_KPASTERISK,1):[("move_group","C"), ("weak_notify","Group","C")], 
                (e.KEY_KPMINUS   ,1):[("move_group","D"), ("weak_notify","Group","D")], 

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

                (e.KEY_KPPLUS,1):[("interrupt",)],
                (e.KEY_KPENTER,1):[("interrupt",), ("move_state","stateMore"), ("notify","Recording","...",1)],
                (e.KEY_KPDOT,1):[("show_help",)],
            },

            # State More. 
            # Macro keys will be recorded when pressed.

            "stateMore": 
            {
                (e.KEY_KP0,1):[("record","0"), ("move_state","stateRec"), ("notify","Recording","{group_name}0",1)], 
                (e.KEY_KP1,1):[("record","1"), ("move_state","stateRec"), ("notify","Recording","{group_name}1",1)],
                (e.KEY_KP2,1):[("record","2"), ("move_state","stateRec"), ("notify","Recording","{group_name}2",1)],
                (e.KEY_KP3,1):[("record","3"), ("move_state","stateRec"), ("notify","Recording","{group_name}3",1)],
                (e.KEY_KP4,1):[("record","4"), ("move_state","stateRec"), ("notify","Recording","{group_name}4",1)],
                (e.KEY_KP5,1):[("record","5"), ("move_state","stateRec"), ("notify","Recording","{group_name}5",1)],
                (e.KEY_KP6,1):[("record","6"), ("move_state","stateRec"), ("notify","Recording","{group_name}6",1)],
                (e.KEY_KP7,1):[("record","7"), ("move_state","stateRec"), ("notify","Recording","{group_name}7",1)],
                (e.KEY_KP8,1):[("record","8"), ("move_state","stateRec"), ("notify","Recording","{group_name}8",1)],
                (e.KEY_KP9,1):[("record","9"), ("move_state","stateRec"), ("notify","Recording","{group_name}9",1)],

                (e.KEY_KPENTER,0):[("move_state", "stateIdle"), ("notify","Recording","",0)],
            },

            # State Rec. 
            # Macro will be saved if DOT is pressed. 
            # Keys 0, 1, 2, and 3 will add delay (0.01, 0.1, 1, 10) seconds
            # Enter will cancel the recording

            "stateRec": 
            {
                (e.KEY_KP0,1):[("wait",  0.01), ("weak_notify", "Delay", "0.01")], 
                (e.KEY_KP1,1):[("wait",  0.1), ("weak_notify", "Delay", "0.1")],
                (e.KEY_KP2,1):[("wait",  1), ("weak_notify", "Delay", "1")],
                (e.KEY_KP3,1):[("wait", 10), ("weak_notify", "Delay", "10")],

                (e.KEY_KPENTER,1):[("save",), ("move_state", "stateIdle"), ("notify","Recording","",0)],
                (e.KEY_KPPLUS,1):[("cancel",), ("move_state", "stateIdle"), ("notify","Recording","",0)],
                (e.KEY_KPDOT,1):[("show_help",)],
            },
        },
    },
}

def format_key_event(event):

    virtual_device_event = VirtualDeviceEvent.bycode(event[0])
    code  = e.bytype[event[1]][event[2]]
    type  = e.EV[event[1]]
    value = event[3]
    source = event[4]

    return f"VirtualDeviceEvent={virtual_device_event}, type={type}, code={code}, value={value}, source={source}"


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

    def play(self, macro, repeat):
        if self.producer.acquire(blocking=False):
            self.task = ("play", macro, repeat)
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
                    self._play(*task_args)

                else:
                    log.debug("Invalid task type: ", task_type)
            
            except:
                traceback.print_exc()
                log.error("MacroPlayer: task failed: ", task_type, task_args)

            self.producer.release()
    
    def _play(self, macro:Macro, repeat):
        
        if not self.stop.locked():
            self.stop.acquire()

        self.mind.emit(TOPIC_NOTIFICATION_STRONG, ("Playing", macro.name, 1))

        try:

            for r in range(repeat):

                log.debug(f"MacroPlayer: Repeating play loop {r+1}/{repeat}, length {len(macro.sequence)}")

                for cmd in macro.sequence:

                    if not self.stop.locked():
                        self.stop.acquire()
                        return

                    cmd_type = cmd[0]
                    cmd_args = cmd[1:]

                    # log.debug(f"  Playing cmd {cmd_type} with args {cmd_args}")

                    if cmd_type == "press_key":
                        if not self._play_press_key(macro, *cmd_args):
                            break

                    elif cmd_type == "wait":
                        if not self._play_wait(macro, *cmd_args):
                            break
                    
                    else:
                        log.debug("Invalid macro cmd: ", cmd_type)
                    
                    # TODO: Required to pause between each playback?
                    # time.sleep(0.01)
        
        except:
            traceback.print_exc()
            log.error("MacroPlayer: cmd failed: ", cmd_type, cmd_args)
        
        self.mind.emit(TOPIC_NOTIFICATION_STRONG, ("Playing", "", 0))

    def _play_press_key(self, macro:Macro, event):
        
        log.debug("  MacroPlayer: Sending key press event to DeviceWriter:", format_key_event(event))
        
        with VirtualKeyboardEvent(self.mind, SOURCE_MACRO_KEYBOARD) as eb:
            eb.forward(event[1], event[2], event[3])

        return True
    
    def _play_wait(self, macro:Macro, seconds):

        log.debug(f"  MacroPlayer: Simulating wait event for {seconds} seconds")
        
        if seconds <= 0.1:
            time.sleep(seconds)
            return True
        
        expire = time.time() + seconds

        while time.time() < expire:
            if not self.stop.locked():
                self.stop.acquire()
                return False

            time.sleep(0.1)

        return True

    def interrupt(self):
        if self.stop.locked():
            self.stop.release()

    def terminate(self):
        self.done = True
        self.consumer.release()


class MacroKeyboard(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)

        self.macro_player = MacroPlayer(self.mind)
        self.userdisplay = None
        self.username = None
        self.recorded = {}
        self.macro = None

        self.import_macros()

        # Monitor current user name and display - needed to open the help screen
        self.add_listener(TOPIC_LOGIN_CHANGED, self.on_login_changed)

        # Monitor output keys sent to virtual output device - needed to record macros
        self.add_listener(TOPIC_VIRTUALKEYBOARD_EVENT, self.on_output_event)

        # Monitor macro keyboards - needed to receive macro keys
        for device_name in MACRO_KEYBOARDS.keys():
            self.add_listener("DeviceReader:" + device_name, self.on_macro_event)

    def on_remove(self):
        super().on_remove()
        self.macro_player.terminate()
    
    def on_login_changed(self, topic_name, event):

        if len(event) == 0:
            self.username, self.userdisplay = None, None
        else:
            self.username, self.userdisplay = event[0]

        log.info("Macro Keyboard received a login changed received", self.username, self.userdisplay)

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

                    elif action[0] == "show_help":
                        self.macro_help()

                    elif action[0] == "notify":
                        self.notify_strong(device_name, action[1], action[2], action[3])

                    elif action[0] == "weak_notify":
                        self.notify_weak(device_name, action[1], action[2])

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
    
    def macro_help(self):
        log.info("Showing help")

        imgpath = os.path.join(os.path.abspath('.'), 'images', 'help_numpad_as_macro_kbd.png')
        cmd = f"su {self.username} -c 'DISPLAY={self.userdisplay} xdg-open {imgpath}'"
        self.thread_help = threading.Thread(target=os.system, args=(cmd,))
        self.thread_help.start()
    
    def notify_strong(self, device_name, title, extra, visible):
        log.info("Sending strong notification")

        mem = MACRO_KEYBOARDS[device_name]["mem"]

        context = {
            "group_name": mem["group"],
            "state_name": mem["state"],
        }

        title = title.format(**context)
        extra = extra.format(**context)

        self.mind.emit(TOPIC_NOTIFICATION_STRONG, (title, extra, visible))
    
    def notify_weak(self, device_name, title, extra):
        log.info("Sending weak notification")

        mem = MACRO_KEYBOARDS[device_name]["mem"]

        context = {
            "group_name": mem["group"],
            "state_name": mem["state"],
        }

        title = title.format(**context)
        extra = extra.format(**context)

        self.mind.emit(TOPIC_NOTIFICATION_WEAK, (title, extra))
    
    def macro_push_delay(self, duration):
        if self.macro is None:
            return

        cmd = ("wait", duration)
        self.macro.sequence.append(cmd)

    def macro_play(self, device_name, macro_key, repeat):

        mem = MACRO_KEYBOARDS[device_name]["mem"]
        macro_name = mem["group"] + macro_key if "group" in mem else macro_key

        log.debug("Playing macro - ", macro_name)

        if macro_name in self.recorded:
            macro = self.recorded[macro_name]
            self.macro_player.play(macro, repeat)

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

        # log.debug(f"Saving event to macro '", self.macro.name, "', '", event, "'")

        event2 = (VirtualDeviceEvent.FORWARD, e.EV_SYN, e.SYN_REPORT, 0, source)

        cmd = ("press_key", event)
        self.macro.sequence.append(cmd)

        cmd = ("press_key", event2)
        self.macro.sequence.append(cmd)
    
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
