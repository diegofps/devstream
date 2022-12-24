
from shadows.watch_windows import TOPIC_WINDOW_CHANGED
from shadows.watch_login import TOPIC_LOGIN_CHANGED

from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.virtual_pen import VirtualPenEvent

from subprocess import Popen, PIPE

from keys import DelayedKey, LockableDelayedKey

import shlex
import time
import log
import os
import re


TOPIC_SMARTOUTPUT_EVENT = "Smart Output"

SOURCE_SMART_OUTPUT = "Smart Output"


class SmartOutputEvent:
    
    SEQUENCE = 0
    FUNCTION = 1
    SLEEP    = 2

    def __init__(self, mind, source):
        self.topic    = TOPIC_SMARTOUTPUT_EVENT
        self.source   = source
        self.mind     = mind
        self.sequence = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.emit()
    
    def function(self, function_name, *args):
        event = (SmartOutputEvent.FUNCTION, self.source, function_name, *args)
        self.sequence.append(event)

    def sleep(self, delay):
        event = (SmartOutputEvent.SLEEP, delay, self.source)
        self.sequence.append(event)
    
    def emit(self):
        sequenceLen = len(self.sequence)

        if sequenceLen == 0:
            return
        
        elif sequenceLen == 1:
            self.mind.emit(self.topic, self.sequence[0])

        else:
            event = (SmartOutputEvent.SEQUENCE, self.sequence, self.source)
            self.mind.emit(self.topic, event)


class SmartOutput:

    def __init__(self, shadow):
        super().__init__(shadow)
        
        self.username = None
        self.userdisplay = None

        self.init_keys()

        self.add_listener(TOPIC_LOGIN_CHANGED, self.on_login_changed)
        self.add_listener(TOPIC_WINDOW_CHANGED, self.on_window_changed)
        self.add_listener(TOPIC_SMARTOUTPUT_EVENT, self.on_event)
        
        preferences = {
            "next_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_TAB", "-KEY_TAB"]}],
            },
            "previous_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_LEFTSHIFT", "+KEY_TAB", "-KEY_TAB", "-KEY_LEFTSHIFT"]}],
            },
            "select_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["-KEY_LEFTALT"]}],
            },
            "undo": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_Z", "-KEY_Z", "-KEY_LEFTCTRL"]}],
            },
            "redo": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_Z", "-KEY_Z", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],
            },
            "volume_up": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["KEY_VOLUMEUP"]}],
            },
            "volume_down": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["KEY_VOLUMEDOWN"]}],
            },
            "zoom_in": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_EQUAL", "-KEY_EQUAL", "-KEY_LEFTCTRL"]}],
            },
            "zoom_out": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_MINUS", "-KEY_MINUS", "-KEY_LEFTCTRL"]}],
            },
            "next_tab": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_TAB", "-KEY_TAB", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],

                ["Code", "Terminator", "Org.gnome.Nautilus", "Apache NetBeans IDE 12.5"]: [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_PAGEUP", "-KEY_PAGEUP", "-KEY_LEFTCTRL"]}],
                
                "Gedit": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTALT", "+KEY_PAGEUP", "-KEY_PAGEUP", "-KEY_LEFTALT", "-KEY_LEFTCTRL"]}],

                "Treesheets": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_V", "-KEY_V", "-KEY_LEFTALT", "+KEY_P", "-KEY_P"]}],
            },
            "previous_tab": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_TAB", "-KEY_TAB", "-KEY_LEFTCTRL"]}],

                ["Code", "Terminator", "Org.gnome.Nautilus", "Apache NetBeans IDE 12.5"]: [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_PAGEDOWN", "-KEY_PAGEDOWN", "-KEY_LEFTCTRL"]}],
                
                "Gedit": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTALT", "+KEY_PAGEDOWN", "-KEY_PAGEDOWN", "-KEY_LEFTALT", "-KEY_LEFTCTRL"]}],

                "Treesheets": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_V", "-KEY_V", "-KEY_LEFTALT", "+KEY_N", "-KEY_N"]}],
            },
            "close_tab": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_W", "-KEY_W", "-KEY_LEFTCTRL"]}],

                ["Terminator", "Gnome-terminal"]: [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_W", "-KEY_W", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],
            },
            "close_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_F4", "-KEY_F4", "-KEY_LEFTALT"]}],
            },
            "navigate_back": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+BTN_SIDE", "-BTN_SIDE"]}],

                "Apache NetBeans IDE 12.5": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_LEFT", "-KEY_LEFT", "-KEY_LEFTALT"]}],
            },
            "navigate_forward": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+BTN_EXTRA", "-BTN_EXTRA"]}],

                "Apache NetBeans IDE 12.5": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_RIGHT", "-KEY_RIGHT", "-KEY_LEFTALT"]}],
            },
            "reopen_tab": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_T", "-KEY_T", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],
            },
            "new_tab": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_T", "-KEY_T", "-KEY_LEFTCTRL"]}],

                ["Code", "Apache NetBeans IDE 12.5", "Dia", "Inkscape", "QtCreator", "Joplin", "Treesheets"]: [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_N", "-KEY_N", "-KEY_LEFTCTRL"]}],

                "Terminator": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_T", "-KEY_T", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],
            },
            "go_to_declaration": {
                "default": [
                    {"type": "keyboard", 
                    "sequence": ["+KEY_LEFTCTRL"]},
                    
                    {"type": "mouse", 
                    "sequence": ["+BTN_LEFT", 0.25, "-BTN_LEFT"]},
                    
                    {"type": "keyboard", 
                    "sequence": ["-KEY_LEFTCTRL"]},
                ],
            },
            "advanced_search": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_F", "-KEY_F", "-KEY_LEFTCTRL"]}],

                ["firefox", "firefox-beta", "QtCreator"]: [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_K", "-KEY_K", "-KEY_LEFTCTRL"]}],

                "Joplin": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_P", "-KEY_P", "-KEY_LEFTCTRL"]}],

                "Gedit": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_H", "-KEY_H", "-KEY_LEFTCTRL"]}],

                "jetbrains-studio": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_N", 0.1, "-KEY_N", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],

                "Code": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_O", "-KEY_O", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],

                "Google-chrome": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_A", "-KEY_A", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],

                ["Gnome-terminal", "Terminator"]: [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_F", "-KEY_F", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],

                "Apache NetBeans IDE 12.5": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_LEFTSHIFT", "+KEY_O", "-KEY_O", "-KEY_LEFTSHIFT", "-KEY_LEFTALT"]}],
            },

            "search_selection": {
                "default": self.search_selection_1,

                ["firefox", "firefox-beta", "Google-chrome"]: [
                    {"type": "keyboard",
                    "sequence": ["+KEY_LEFTALT"]},

                    {"type": "mouse",
                    "sequence": ["+BTN_RIGHT", "-BTN_RIGHT", 0.2]},

                    {"type": "keyboard",
                    "sequence": ["-KEY_LEFTALT", "+KEY_S", "+KEY_S"]}],
            },
            "scroll_h": {
                "default": self.scroll_h_1,
                ["Dia", "Inkscape"]: self.scroll_h_2,
                "Google-chrome": self.scroll_h_3,
            },
            "scroll_v": {
                "default": self.scroll_v_1,
                ["Dia", "Inkscape"]: self.scroll_v_2,
                "Google-chrome": self.scroll_v_3,
            },
        }

        # Convert list of names to single names

        self.preferences = {}
        for function_name, options in preferences.items():
            self.preferences[function_name] = {}
            for app_name_or_list, events in options.items():
                if isinstance(app_name_or_list, list):
                    for app_name in app_name_or_list:
                        self.preferences[function_name][app_name] = events
                else:
                    self.preferences[function_name][app_name_or_list] = events
        
        # Configure initial current functions as the default function

        self.functions = {k: v["default"] for k, v in self.preferences.items()}


    def run(self, function_name, *args):
        if not function_name in self.functions:
            log.error("Unknown function: %s", function_name)
            return
        
        function = self.functions[function_name]

        if isinstance(function, list):
            for f in function:
                if f["type"] == "keyboard":
                    VirtualEvent = VirtualKeyboardEvent
                elif f["type"] == "mouse":
                    VirtualEvent = VirtualMouseEvent
                else:
                    log.error(f"Unknown function type: {f['type']}")
                    continue
                
                with VirtualEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                    for key in f["sequence"]:
                        if isinstance(key, (int, float)):
                            eb.sleep(key)
                        elif key.startswith("+"):
                            eb.press(key[1:])
                        elif key.startswith("-"):
                            eb.release(key[1:])
                        else:
                            eb.press(key)
                            eb.release(key)
        else:
            function(*args)

    def init_keys(self):

        self.SCROLL_VOLUME  = DelayedKey("SCROLL_VOLUME",  lambda v: self.run("volume_up") if v else self.run("volume_down"), 200)
        self.SCROLL_TABS    = DelayedKey("SCROLL_TABS",    lambda v: self.run("next_tab") if v else self.run("previous_tab"), 500)
        self.SCROLL_WINDOWS = DelayedKey("SCROLL_WINDOWS", lambda v: self.run("next_window") if v else self.run("previous_window"), 500)
        self.SCROLL_ZOOM    = DelayedKey("SCROLL_ZOOM",    lambda v: self.run("zoom_in") if v else self.run("zoom_out"), 200)
        self.SCROLL_UNDO    = DelayedKey("SCROLL_UNDO",    lambda v: self.run("undo") if v else self.run("redo"), 200)

        self.DUAL_WINDOWS_TABS = LockableDelayedKey(
                "DUAL_WINDOWS_TABS", 
                lambda v: self.run("next_window") if v else self.run("previous_window"), 
                lambda v: self.run("next_tab") if v else self.run("previous_tab"),
                800) # lockable1
        
        self.DUAL_UNDO_VOLUME  = LockableDelayedKey(
                "DUAL_UNDO_VOLUME",  
                lambda v: self.run("navigate_back") if v else self.run("navigate_forward"),
                lambda v: self.run("volume_up") if v else self.run("volume_down"), 
                500) # lockable2
    
    def on_event(self, topic_name, event):
        event_type = event[0]

        if event_type == SmartOutputEvent.SEQUENCE:
            for event2 in event[1]:
                self.on_event(topic_name, event2)
        
        elif event_type == SmartOutputEvent.FUNCTION:
            function_name = event[2]
            params = event[3:]
            self.run(function_name, *params)

        elif event_type == SmartOutputEvent.SLEEP:
            delay = event[1]
            time.sleep(delay)
        
        else:
            log.error(f"Invalid event_type in {self.__class__.__name__} event: {event_type}")

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

    def scroll_h_1(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_H", value * 20)
    
    def scroll_v_1(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_V", value * -10)
    
    def scroll_h_2(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_H", value * 5)
    
    def scroll_v_2(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_V", value * -5)
    
    def scroll_h_3(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_H", value * 10)
    
    def scroll_v_3(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_V", value * -10)
    

def on_load(shadow):
    SmartOutput(shadow)

