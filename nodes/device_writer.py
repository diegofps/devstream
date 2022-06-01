from keys import Key, WheelKey, DirectKey, DelayedKey, LockableDelayedKey
from utils import warn, error, info, debug, BaseNode
from nodes.watch_windows import TOPIC_WINDOW_CHANGED
from evdev import AbsInfo, UInput, ecodes as e

import time


TOPIC_DEVICEWRITER_EVENT = "DeviceWriter"


class OutputEvent:

    PRESS    = 0
    RELEASE  = 1
    UPDATE   = 2
    UPDATE_H = 3
    UPDATE_V = 4
    UNLOCK   = 5
    FORWARD  = 6
    # FUNCTION = 7
    SLEEP    = 8
    SEQUENCE = 9

    def __init__(self, core):
        self.sequence = []
        self.core = core
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.emit()
    
    def press(self, key_name):
        event = (OutputEvent.PRESS, key_name)
        self.sequence.append(event)

    def release(self, key_name):
        event = (OutputEvent.RELEASE, key_name)
        self.sequence.append(event)

    def update(self, key_name, value):
        event = (OutputEvent.UPDATE, key_name, value)
        self.sequence.append(event)

    def update_h(self, key_name, value):
        event = (OutputEvent.UPDATE_H, key_name, value)
        self.sequence.append(event)

    def update_v(self, key_name, value):
        event = (OutputEvent.UPDATE_V, key_name, value)
        self.sequence.append(event)

    def unlock(self, key_name):
        event = (OutputEvent.UNLOCK, key_name)
        self.sequence.append(event)

    def forward(self, type, code, value):
        event = (OutputEvent.FORWARD, type, code, value)
        self.sequence.append(event)

    # def function(self, function_name, *args):
    #     event = (OutputEvent.FUNCTION, function_name, *args)
    #     self.sequence.append(event)

    def sleep(self, delay):
        event = (OutputEvent.SLEEP, delay)
        self.sequence.append(event)
    
    def emit(self):
        sequenceLen = len(self.sequence)
        if sequenceLen == 0:
            return
        
        elif sequenceLen == 1:
            self.core.emit(TOPIC_DEVICEWRITER_EVENT, self.sequence[0])

        else:
            event = (OutputEvent.SEQUENCE, self.sequence)
            self.core.emit(TOPIC_DEVICEWRITER_EVENT, event)


class DeviceWriter(BaseNode):

    def __init__(self, core):
        super().__init__(core, "DeviceWriter")
        
        self.init_virtual_device()
        self.init_keys()

        self.core.register_listener(TOPIC_WINDOW_CHANGED, self.on_window_changed)
        self.core.register_listener(TOPIC_DEVICEWRITER_EVENT, self.on_event)

    def on_window_changed(self, topic_name, event):
        debug("receiving window changed event in DeviceWriter", topic_name, event)

    def init_virtual_device(self):

        cap = {
            e.EV_KEY : [
                e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, 

                e.KEY_LEFTALT, e.KEY_LEFTCTRL, e.KEY_LEFTSHIFT, e.KEY_LEFTMETA, 
                e.KEY_RIGHTALT, e.KEY_RIGHTCTRL, e.KEY_RIGHTSHIFT, e.KEY_RIGHTMETA, 
                e.KEY_TAB, e.KEY_PAGEUP, e.KEY_PAGEDOWN, e.KEY_PRINT, e.KEY_HOME, e.KEY_END, 
                e.KEY_MINUS, e.KEY_EQUAL, e.KEY_ESC, e.KEY_COMMA, e.KEY_SLASH, e.KEY_DOT, 
                e.KEY_APOSTROPHE, e.KEY_BACKSLASH, e.KEY_LEFTBRACE, e.KEY_RIGHTBRACE, 
                e.KEY_SEMICOLON, e.KEY_SPACE, e.KEY_CAPSLOCK, e.KEY_GRAVE, e.KEY_SCROLLLOCK, 
                e.KEY_SYSRQ, e.KEY_PAUSE, e.KEY_DELETE, e.KEY_INSERT, e.KEY_RO, e.KEY_BACKSPACE, 
                e.KEY_LEFT, e.KEY_RIGHT, e.KEY_UP, e.KEY_DOWN, e.KEY_ENTER, e.KEY_102ND, 

                e.KEY_0, e.KEY_1, e.KEY_2, e.KEY_3, e.KEY_4, e.KEY_5, e.KEY_6, e.KEY_7, e.KEY_8, e.KEY_9, 

                e.KEY_A, e.KEY_B, e.KEY_C, e.KEY_D, e.KEY_E, e.KEY_F, e.KEY_G, e.KEY_H, e.KEY_I, 
                e.KEY_J, e.KEY_K, e.KEY_L, e.KEY_M, e.KEY_N, e.KEY_O, e.KEY_P, e.KEY_Q, e.KEY_R, 
                e.KEY_S, e.KEY_T, e.KEY_U, e.KEY_V, e.KEY_W, e.KEY_X, e.KEY_Y, e.KEY_Z, 

                e.KEY_F1, e.KEY_F2, e.KEY_F3, e.KEY_F4, e.KEY_F5, e.KEY_F6, 
                e.KEY_F7, e.KEY_F8, e.KEY_F9, e.KEY_F10, e.KEY_F11, e.KEY_F12, 

                e.KEY_PLAYPAUSE, e.KEY_NEXTSONG, e.KEY_PREVIOUSSONG, e.KEY_STOPCD, 
                e.KEY_MUTE, e.KEY_VOLUMEUP, e.KEY_VOLUMEDOWN, e.KEY_PRESENTATION, 

            ],

            e.EV_ABS: [
                (e.ABS_X, AbsInfo(value=0, min=0, max=+16384, fuzz=0, flat=0, resolution=0)), 
                (e.ABS_Y, AbsInfo(value=0, min=0, max=+16384, fuzz=0, flat=0, resolution=0)), 
            ],

            e.EV_REL : [
                (e.REL_X, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_Y, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_WHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_HWHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_WHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_HWHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
            ]
        }

        self.vdev = UInput(cap, name="devstream", version=0x3)

        self.acquired_keys = set()
        self.acquired_keys.update(cap[1])
        self.acquired_keys.update([x[0] for x in cap[2]])
        self.acquired_keys.update([x[0] for x in cap[3]])

    def init_keys(self):

        self.ABS_X   = DirectKey("ABS_X",   self.vdev, e.EV_ABS, e.ABS_X)
        self.ABS_Y   = DirectKey("ABS_Y",   self.vdev, e.EV_ABS, e.ABS_Y)
        self.REL_X   = DirectKey("REL_X",   self.vdev, e.EV_REL, e.REL_X)
        self.REL_Y   = DirectKey("REL_Y",   self.vdev, e.EV_REL, e.REL_Y)
        self.WHEEL_H = WheelKey ("WHEEL_H", self.vdev, e.EV_REL, e.REL_HWHEEL, e.REL_HWHEEL_HI_RES, 120)
        self.WHEEL_V = WheelKey ("WHEEL_V", self.vdev, e.EV_REL, e.REL_WHEEL,  e.REL_WHEEL_HI_RES,  120)

        self.SCROLL_VOLUME  = DelayedKey("SCROLL_VOLUME",  self.on_update_volume,  200)
        self.SCROLL_TABS    = DelayedKey("SCROLL_TABS",    self.on_switch_tabs,    500)
        self.SCROLL_WINDOWS = DelayedKey("SCROLL_WINDOWS", self.on_switch_windows, 500)
        self.SCROLL_ZOOM    = DelayedKey("SCROLL_ZOOM",    self.on_switch_zoom,    200)
        self.SCROLL_UNDO    = DelayedKey("SCROLL_UNDO",    self.on_undo_redo,      200)

        self.DUAL_WINDOWS_TABS = LockableDelayedKey("DUAL_WINDOWS_TABS", self.on_switch_windows, self.on_switch_tabs,   800) # lockable1
        self.DUAL_UNDO_VOLUME  = LockableDelayedKey("DUAL_UNDO_VOLUME",  self.on_undo_redo,      self.on_update_volume, 500) # lockable2
    
        self.add_keys([
            ("BTN_RIGHT", 90001), ("BTN_LEFT", 90004), ("BTN_MIDDLE", 90005), ("BTN_SIDE", 90004), ("BTN_EXTRA", 90005), 
            "LEFTALT", "LEFTCTRL", "LEFTMETA", "LEFTSHIFT", "RIGHTALT", "RIGHTCTRL", "RIGHTMETA", "RIGHTSHIFT", "TAB", "PAGEDOWN", "PAGEUP",
            "PLAYPAUSE", "NEXTSONG", "PREVIOUSSONG", "STOPCD", "MUTE", "VOLUMEUP", "VOLUMEDOWN", "EQUAL", "MINUS", "ESC",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
        ])

    def on_event(self, topic_name, event):
        # debug("DevideWriter received an event:", topic_name, event)
        event_type = event[0]

        if event_type == OutputEvent.SEQUENCE:
            for event2 in event[1]:
                self.on_event(topic_name, event2)
        
        elif event_type == OutputEvent.PRESS:
            key_name = event[1]
            if hasattr(self, key_name):
                getattr(self, key_name).press()
        
        elif event_type == OutputEvent.RELEASE:
            key_name = event[1]
            if hasattr(self, key_name):
                getattr(self, key_name).release()
        
        elif event_type == OutputEvent.UPDATE:
            key_name = event[1]
            value = event[2]
            if hasattr(self, key_name):
                getattr(self, key_name).update(value)
        
        elif event_type == OutputEvent.UPDATE_H:
            key_name = event[1]
            value = event[2]
            if hasattr(self, key_name):
                getattr(self, key_name).update_h(value)
        
        elif event_type == OutputEvent.UPDATE_V:
            key_name = event[1]
            value = event[2]
            if hasattr(self, key_name):
                getattr(self, key_name).update_v(value)
        
        elif event_type == OutputEvent.UNLOCK:
            key_name = event[1]
            if hasattr(self, key_name):
                getattr(self, key_name).unlock()
        
        elif event_type == OutputEvent.FORWARD:
            type = event[1]
            code = event[2]
            value = event[3]

            if not code in self.acquired_keys:
                error("Missing key", e.KEY[code])
            
            self.vdev.write(type, code, value)
        
        # elif event_type == OutputEvent.FUNCTION:
        #     function_name = event[1]
            
        #     if hasattr(self, function_name):
        #         params = event[2:]
        #         getattr(self, function_name)(*params)
        
        elif event_type == OutputEvent.SLEEP:
            delay = event[1]
            time.sleep(delay)
        
        else:
            error("Invalid event_type in DeviceWriter event:", event_type)

    # def control_left_click(self):

    #     self.KEY_LEFTCTRL.press()
    #     self.BTN_LEFT.press()

    #     time.sleep(0.25) # The click must happen after the IDE has created the "button"

    #     self.BTN_LEFT.release()
    #     self.KEY_LEFTCTRL.release()
    
    # def search_selection(self):

    #     self.KEY_LEFTALT.press()

    #     self.BTN_RIGHT.press()
    #     self.BTN_RIGHT.release()

    #     time.sleep(0.2)

    #     self.KEY_LEFTALT.release()

    #     self.KEY_S.press()
    #     self.KEY_S.release()
        
    def on_undo_redo(self, value):
        if value:
            self.KEY_LEFTCTRL.press()
            self.KEY_LEFTSHIFT.press()
            self.KEY_Z.press()
            self.KEY_Z.release()
            self.KEY_LEFTSHIFT.release()
            self.KEY_LEFTCTRL.release()

        else:
            self.KEY_LEFTCTRL.press()
            self.KEY_Z.press()
            self.KEY_Z.release()
            self.KEY_LEFTCTRL.release()
    
    def on_switch_zoom(self, value):
        if value:
            self.KEY_LEFTCTRL.press()
            self.KEY_EQUAL.press()
            self.KEY_EQUAL.release()
            self.KEY_LEFTCTRL.release()

        else:
            self.KEY_LEFTCTRL.press()
            self.KEY_MINUS.press()
            self.KEY_MINUS.release()
            self.KEY_LEFTCTRL.release()
    
    def on_switch_tabs(self, value):
        if value:
            self.KEY_LEFTCTRL.press()
            self.KEY_LEFTSHIFT.press()
            self.KEY_TAB.press()
            self.KEY_TAB.release()
            self.KEY_LEFTSHIFT.release()
            self.KEY_LEFTCTRL.release()

        else:
            self.KEY_LEFTCTRL.press()
            self.KEY_TAB.press()
            self.KEY_TAB.release()
            self.KEY_LEFTCTRL.release()
    
    def on_switch_windows(self, value):
        self.KEY_LEFTALT.press()
        
        if value:
            self.KEY_TAB.press()
            self.KEY_TAB.release()

        else:
            self.KEY_LEFTSHIFT.press()
            self.KEY_TAB.press()
            self.KEY_TAB.release()
            self.KEY_LEFTSHIFT.release()
    
    def on_update_volume(self, value):
        if value:
            self.KEY_VOLUMEUP.press()
            self.KEY_VOLUMEUP.release()

        else:
            self.KEY_VOLUMEDOWN.press()
            self.KEY_VOLUMEDOWN.release()

    # def on_forward(self, event):
    #     if not event.code in self.acquired_keys:
    #         error("Missing key", e.KEY[event.code])
    #     self.vdev.write(event.type, event.code, event.value)

    def terminate(self):
        if self.vdev is not None:
            self.vdev.close()

    def add_keys(self, names):
        for name in names:
            if isinstance(name, tuple):
                name, scan_code = name
            else:
                scan_code = None
            
            name = name if name.startswith("KEY_") or name.startswith("BTN_") else "KEY_" + name
            value = getattr(e, name)
            key = Key(name, self.vdev, e.EV_KEY, value, scan_code)
            setattr(self, name, key)


def on_init(core):
    core.add_node("DeviceWriter", DeviceWriter(core))

