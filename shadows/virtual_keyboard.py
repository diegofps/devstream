from keys import Key, WheelKey, DirectKey, DelayedKey, LockableDelayedKey
from shadows.watch_windows import TOPIC_WINDOW_CHANGED
from shadows.watch_login import TOPIC_LOGIN_CHANGED
from evdev import AbsInfo, UInput, ecodes as e
from subprocess import Popen, PIPE
from reflex import Reflex

import shlex
import time
import log
import os
import re


TOPIC_DEVICEWRITER_EVENT = "DeviceWriter"


class OutputEvent:

    PRESS    = 0
    RELEASE  = 1
    UPDATE   = 2
    UPDATE_H = 3
    UPDATE_V = 4
    UNLOCK   = 5
    FORWARD  = 6
    FUNCTION = 7
    SLEEP    = 8
    SEQUENCE = 9

    def __init__(self, mind, topic=TOPIC_DEVICEWRITER_EVENT, source=None):
        self.sequence = []
        self.topic = topic
        self.mind = mind
        self.source = source
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.emit()
    
    def press(self, key_name):
        event = (OutputEvent.PRESS, key_name, self.source)
        self.sequence.append(event)

    def release(self, key_name):
        event = (OutputEvent.RELEASE, key_name, self.source)
        self.sequence.append(event)

    def update(self, key_name, value):
        event = (OutputEvent.UPDATE, key_name, value, self.source)
        self.sequence.append(event)

    def update_h(self, key_name, value):
        event = (OutputEvent.UPDATE_H, key_name, value, self.source)
        self.sequence.append(event)

    def update_v(self, key_name, value):
        event = (OutputEvent.UPDATE_V, key_name, value, self.source)
        self.sequence.append(event)

    def unlock(self, key_name):
        event = (OutputEvent.UNLOCK, key_name, self.source)
        self.sequence.append(event)

    def forward(self, type, code, value):
        event = (OutputEvent.FORWARD, type, code, value, self.source)
        self.sequence.append(event)

    def function(self, function_name, *args):
        event = (OutputEvent.FUNCTION, self.source, function_name, *args)
        self.sequence.append(event)

    def sleep(self, delay):
        event = (OutputEvent.SLEEP, delay, self.source)
        self.sequence.append(event)
    
    def emit(self):
        sequenceLen = len(self.sequence)

        if sequenceLen == 0:
            return
        
        elif sequenceLen == 1:
            self.mind.emit(self.topic, self.sequence[0])

        else:
            event = (OutputEvent.SEQUENCE, self.sequence, self.source)
            self.mind.emit(self.topic, event)


class Shortcut:

    def __init__(self, writer, *args):
        self.keys = [getattr(writer, "KEY_" + x) if isinstance(x,str) else x for x in args]
    
    def __call__(self):
        for key in self.keys:
            if isinstance(key, float):
                time.sleep(key)
            else:
                key.press()
        
        for key in reversed(self.keys):
            if isinstance(key, float):
                time.sleep(key)
            else:
                key.release()


class VirtualKeyboard(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        
        self.username = None
        self.userdisplay = None

        self.init_virtual_device()
        self.init_keys()

        self.add_listener(TOPIC_LOGIN_CHANGED, self.on_login_changed)
        self.add_listener(TOPIC_WINDOW_CHANGED, self.on_window_changed)
        self.add_listener(TOPIC_DEVICEWRITER_EVENT, self.on_event)

        self.preferred_change_windows = {}
        self.preferred_change_history = {}
        self.preferred_change_volume = {}
        self.preferred_change_zoom = {}
        self.preferred_change_tabs = {
            "Code": self.change_tabs_2,
            "Terminator": self.change_tabs_2,
            "Gedit": self.change_tabs_3,
            "Org.gnome.Nautilus": self.change_tabs_2,
            "Apache NetBeans IDE 12.5": self.change_tabs_2,
            "Treesheets": self.change_tabs_4, 
        }
        self.preferred_close_tab = {
            "Terminator": self.close_tab_2,
            "Gnome-terminal": self.close_tab_2,
        }
        self.preferred_close_window = {}
        self.preferred_navigate_back = {
            "Apache NetBeans IDE 12.5": self.navigate_back_2
        }
        self.preferred_navigate_forward = {
            "Apache NetBeans IDE 12.5": self.navigate_forward_2
        }
        self.preferred_reopen_tab = {}
        self.preferred_new_tab = {
            "Code": self.new_tab_2,
            "Apache NetBeans IDE 12.5": self.new_tab_2,
            "Terminator": self.new_tab_3,
            "Dia": self.new_tab_2,
            "Inkscape": self.new_tab_2,
            "QtCreator": self.new_tab_2,
            "Joplin": self.new_tab_2,
            "Treesheets": self.new_tab_2, 
        }
        self.preferred_go_to_declaration = {}
        self.preferred_search_selection = {
            "firefox": self.search_selection_2,
            "firefox-beta": self.search_selection_2,
            "Google-chrome": self.search_selection_2,
        }
        self.preferred_advanced_search = {
            "jetbrains-studio": Shortcut(self, "LEFTCTRL", "LEFTSHIFT", "N", 0.1),
            "Code": Shortcut(self, "LEFTCTRL", "LEFTSHIFT", "O"),
            "QtCreator": Shortcut(self, "LEFTCTRL", "K"),
            "Apache NetBeans IDE 12.5": Shortcut(self, "LEFTALT", "LEFTSHIFT", "O"),
            "Joplin": Shortcut(self, "LEFTCTRL", "P"),
            "Google-chrome": Shortcut(self, "LEFTCTRL", "LEFTSHIFT", "A"),
            "firefox": Shortcut(self, "LEFTCTRL", "K"),
            "firefox-beta": Shortcut(self, "LEFTCTRL", "K"),
            "Gedit": Shortcut(self, "LEFTCTRL", "H"),
            "Terminator": Shortcut(self, "LEFTCTRL", "LEFTSHIFT", "F"),
            "Gnome-terminal": Shortcut(self, "LEFTCTRL", "LEFTSHIFT", "F"),
            "Org.gnome.Nautilus": self.advanced_search_1,
        }
        self.preferred_scroll_h = {
            "Dia": self.scroll_h_2,
            "Inkscape": self.scroll_h_2,
            "Google-chrome": self.scroll_h_3,
        }
        self.preferred_scroll_v = {
            "Dia": self.scroll_v_2,
            "Inkscape": self.scroll_v_2,
            "Google-chrome": self.scroll_v_3,
        }

        # Now we declare function_names and the default functions
        self.function_names = [attr[10:] for attr in dir(self) if attr.startswith('preferred_')]

        for name in self.function_names:
            callback = getattr(self, name + '_1')

            if callback is None:
                log.error(f"Missing default function for {name}")
            else:
                setattr(self, 'function_' + name, callback)

    def on_login_changed(self, topic_name, event):
        if len(event) == 0:
            self.username, self.userdisplay = None, None
        else:
            self.username, self.userdisplay = event[0]
        log.info("login changed received", self.username, self.userdisplay)

    def on_window_changed(self, topic_name, event):
        window_class, app_name, window_name = event

        for intent_name in self.function_names:
            preferred_intents = getattr(self, "preferred_" + intent_name)

            if app_name in preferred_intents:
                callback = preferred_intents[app_name]
                setattr(self, "function_" + intent_name, callback) 
            else:
                callback = getattr(self, intent_name + "_1")
                setattr(self, "function_" + intent_name, callback)
        
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

                # e.KEY_KP0, e.KEY_KP1, e.KEY_KP2, e.KEY_KP3, e.KEY_KP4, e.KEY_KP5, e.KEY_KP6, e.KEY_KP7, e.KEY_KP8, e.KEY_KP9,
                # e.KEY_KPMINUS, e.KEY_KPPLUS, e.KEY_KPENTER, e.KEY_KPDOT, e.KEY_KPSLASH, e.KEY_KPASTERISK, e.KEY_NUMLOCK,

                # e.BTN_TOOL_PEN, e.BTN_STYLUS, e.BTN_TOUCH,

            ],

            e.EV_ABS: [
                # (e.ABS_X, AbsInfo(value=0, min=0, max=+32767, fuzz=0, flat=0, resolution=0)), 
                # (e.ABS_Y, AbsInfo(value=0, min=0, max=+32767, fuzz=0, flat=0, resolution=0)), 
                # (e.ABS_PRESSURE, AbsInfo(value=0, min=0, max=+8191, fuzz=0, flat=0, resolution=0)), 
                # (e.ABS_TILT_X, AbsInfo(value=0, min=-127, max=+127, fuzz=0, flat=0, resolution=0)), 
                # (e.ABS_TILT_Y, AbsInfo(value=0, min=-127, max=+127, fuzz=0, flat=0, resolution=0)), 
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

        self.SCROLL_VOLUME  = DelayedKey("SCROLL_VOLUME",  lambda v: self.function_change_volume(v),  200)
        self.SCROLL_TABS    = DelayedKey("SCROLL_TABS",    lambda v: self.function_change_tabs(v),    500)
        self.SCROLL_WINDOWS = DelayedKey("SCROLL_WINDOWS", lambda v: self.function_change_windows(v), 500)
        self.SCROLL_ZOOM    = DelayedKey("SCROLL_ZOOM",    lambda v: self.function_change_zoom(v),    200)
        self.SCROLL_UNDO    = DelayedKey("SCROLL_UNDO",    lambda v: self.function_change_history(v), 200)

        self.DUAL_WINDOWS_TABS = LockableDelayedKey(
                "DUAL_WINDOWS_TABS", 
                lambda v: self.function_change_windows(v), 
                lambda v: self.function_change_tabs(v),
                800) # lockable1
        
        self.DUAL_UNDO_VOLUME  = LockableDelayedKey(
                "DUAL_UNDO_VOLUME",  
                lambda v: self.function_change_history(v),      
                lambda v: self.function_change_volume(v), 
                500) # lockable2
    
        self.add_keys([
            ("BTN_RIGHT", 90001), ("BTN_LEFT", 90004), ("BTN_MIDDLE", 90005), ("BTN_SIDE", 90004), ("BTN_EXTRA", 90005), 
            "LEFTALT", "LEFTCTRL", "LEFTMETA", "LEFTSHIFT", "RIGHTALT", "RIGHTCTRL", "RIGHTMETA", "RIGHTSHIFT", 
            "PLAYPAUSE", "NEXTSONG", "PREVIOUSSONG", "STOPCD", "MUTE", "VOLUMEUP", "VOLUMEDOWN", 

            "TAB", "PAGEDOWN", "PAGEUP", "EQUAL", "MINUS", "ESC",
            "PRINT", "HOME", "END", "COMMA", "SLASH", "DOT", 
            "APOSTROPHE", "BACKSLASH", "LEFTBRACE", "RIGHTBRACE", 
            "SEMICOLON", "SPACE", "CAPSLOCK", "GRAVE", "SCROLLLOCK", 
            "SYSRQ", "PAUSE", "DELETE", "INSERT", "RO", "BACKSPACE", 
            "LEFT", "RIGHT", "UP", "DOWN", "ENTER", "102ND", 

            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",

            "KP0", "KP1", "KP2", "KP3", "KP4", "KP5", "KP6", "KP7", "KP8", "KP9",
            "KPMINUS", "KPPLUS", "KPENTER", "KPDOT", "KPSLASH", "KPASTERISK", "NUMLOCK",
        ])

        

    def on_event(self, topic_name, event):
        # log.debug("Processing DeviceWriter event", event)
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
            type  = event[1]
            code  = event[2]
            value = event[3]

            if not code in self.acquired_keys:
                log.info("VirtualKeyboard is ignoring key", e.KEY[code])
            
            self.vdev.write(type, code, value)
        
        elif event_type == OutputEvent.FUNCTION:
            function_name = "function_" + event[2]
            
            if hasattr(self, function_name):
                params = event[3:]
                getattr(self, function_name)(*params)
        
        elif event_type == OutputEvent.SLEEP:
            delay = event[1]
            time.sleep(delay)
        
        else:
            log.error("Invalid event_type in DeviceWriter event:", event_type)

    def change_history_1(self, value):
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
    
    def change_tabs_1(self, value):
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
    
    def change_tabs_2(self, value):
        if value:
            self.KEY_LEFTCTRL.press()
            self.KEY_PAGEUP.press()
            self.KEY_PAGEUP.release()
            self.KEY_LEFTCTRL.release()

        else:
            self.KEY_LEFTCTRL.press()
            self.KEY_PAGEDOWN.press()
            self.KEY_PAGEDOWN.release()
            self.KEY_LEFTCTRL.release()
    
    def change_tabs_3(self, value):
        if value:
            self.KEY_LEFTCTRL.press()
            self.KEY_LEFTALT.press()
            self.KEY_PAGEUP.press()
            self.KEY_PAGEUP.release()
            self.KEY_LEFTALT.release()
            self.KEY_LEFTCTRL.release()

        else:
            self.KEY_LEFTCTRL.press()
            self.KEY_LEFTALT.press()
            self.KEY_PAGEDOWN.press()
            self.KEY_PAGEDOWN.release()
            self.KEY_LEFTALT.release()
            self.KEY_LEFTCTRL.release()
    
    def change_tabs_4(self, value):
        self.KEY_LEFTALT.press()
        self.KEY_V.press()
        self.KEY_V.release()
        self.KEY_LEFTALT.release()
        # time.sleep(0.1)

        if value:
            self.KEY_P.press()
            self.KEY_P.release()

        else:
            self.KEY_N.press()
            self.KEY_N.release()
    
    def change_windows_1(self, value):
        self.KEY_LEFTALT.press()
        
        if value:
            self.KEY_TAB.press()
            self.KEY_TAB.release()

        else:
            self.KEY_LEFTSHIFT.press()
            self.KEY_TAB.press()
            self.KEY_TAB.release()
            self.KEY_LEFTSHIFT.release()
    
    def change_zoom_1(self, value):
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
    
    def change_volume_1(self, value):
        if value:
            self.KEY_VOLUMEUP.press()
            self.KEY_VOLUMEUP.release()

        else:
            self.KEY_VOLUMEDOWN.press()
            self.KEY_VOLUMEDOWN.release()

    def close_tab_1(self):
        self.KEY_LEFTCTRL.press()
        self.KEY_W.press()

        self.KEY_W.release()
        self.KEY_LEFTCTRL.release()
        
    def close_tab_2(self):
        self.KEY_LEFTCTRL.press()
        self.KEY_LEFTSHIFT.press()
        self.KEY_W.press()

        self.KEY_W.release()
        self.KEY_LEFTSHIFT.release()
        self.KEY_LEFTCTRL.release()

    def close_window_1(self):
        self.KEY_LEFTALT.press()
        self.KEY_F4.press()

        self.KEY_F4.release()
        self.KEY_LEFTALT.release()
        
    def navigate_back_1(self):
        self.BTN_SIDE.press()
        self.BTN_SIDE.release()
        
    def navigate_back_2(self):
        self.KEY_LEFTALT.press()
        self.KEY_LEFT.press()

        self.KEY_LEFT.release()
        self.KEY_LEFTALT.release()
    
    def navigate_forward_1(self):
        self.BTN_EXTRA.press()
        self.BTN_EXTRA.release()
        
    def navigate_forward_2(self):
        self.KEY_LEFTALT.press()
        self.KEY_RIGHT.press()

        self.KEY_RIGHT.release()
        self.KEY_LEFTALT.release()
    
    def reopen_tab_1(self):
        self.KEY_LEFTCTRL.press()
        self.KEY_LEFTSHIFT.press()
        self.KEY_T.press()
        
        self.KEY_T.release()
        self.KEY_LEFTSHIFT.release()
        self.KEY_LEFTCTRL.release()
    
    def new_tab_1(self):
        self.KEY_LEFTCTRL.press()
        self.KEY_T.press()
    
        self.KEY_T.release()
        self.KEY_LEFTCTRL.release()

    def new_tab_2(self):
        self.KEY_LEFTCTRL.press()
        self.KEY_N.press()
    
        self.KEY_N.release()
        self.KEY_LEFTCTRL.release()

    def new_tab_3(self):
        self.KEY_LEFTCTRL.press()
        self.KEY_LEFTSHIFT.press()
        self.KEY_T.press()

        self.KEY_T.release()
        self.KEY_LEFTSHIFT.release()
        self.KEY_LEFTCTRL.release()

    def go_to_declaration_1(self):
        self.KEY_LEFTCTRL.press()
        self.BTN_LEFT.press()
        
        time.sleep(0.25)

        self.BTN_LEFT.release()
        self.KEY_LEFTCTRL.release()
    
    def search_selection_1(self):
        log.info("Running search selection 1")
        if self.username is None:
            log.error("Could not find a user session to open this search")
        
        cmd = "su %s -c 'xclip -selection primary -o -l 1 -d %s'" % (self.username, self.userdisplay)
        proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        selection = proc.stdout.read().decode('utf-8')

        query = re.sub('\s', '%20', selection)
        cmd = "su %s -c 'DISPLAY=%s xdg-open http://www.google.com.br/search?q=%s &'" % (self.username, self.userdisplay, query)

        os.system(cmd)
    
    def search_selection_2(self):
        log.info("Running search selection 2")
        self.KEY_LEFTALT.press()
        self.BTN_RIGHT.press()
        self.BTN_RIGHT.release()

        time.sleep(0.2)

        self.KEY_LEFTALT.release()
        self.KEY_S.press()
        self.KEY_S.release()
    
    def advanced_search_1(self):
        self.KEY_LEFTCTRL.press()
        self.KEY_F.press()

        self.KEY_F.release()
        self.KEY_LEFTCTRL.release()
    
    def scroll_h_1(self, value):
        self.WHEEL_H.update(value * 20)
    
    def scroll_v_1(self, value):
        self.WHEEL_V.update(value * -10)
    
    def scroll_h_2(self, value):
        self.WHEEL_H.update(value * 5)
    
    def scroll_v_2(self, value):
        self.WHEEL_V.update(value * -5)
    
    def scroll_h_3(self, value):
        self.WHEEL_H.update(value * 10)
    
    def scroll_v_3(self, value):
        self.WHEEL_V.update(value * -10)
    
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


def on_load(shadow):
    VirtualKeyboard(shadow)

