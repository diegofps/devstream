
from shadows.watch_windows import TOPIC_WINDOW_CHANGED
from shadows.watch_login import TOPIC_LOGIN_CHANGED

from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
# from shadows.virtual_pen import VirtualPenEvent

from keys import DelayedKey, LockableDelayedKey, AdversarialDelayedKey

from subprocess import Popen, PIPE
from shadow import Shadow
from reflex import Reflex

import shlex
import re
import os

TOPIC_SMARTOUTPUT_EVENT = "SmartOutput"
SOURCE_SMART_OUTPUT = "Smart Output"

class SmartOutputEvent:

    FUNCTION = 0
    UPDATE   = 1
    UPDATE_H = 2
    UPDATE_V = 3
    
    def __init__(self, mind, source=None):
        self.topic         = TOPIC_SMARTOUTPUT_EVENT
        self.source        = source
        self.mind          = mind
        self.sequence      = []
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.emit()
    
    def update(self, key_name, *args):
        event = (SmartOutputEvent.UPDATE, key_name, args)
        self.sequence.append(event)
    
    def update_h(self, key_name, *args):
        event = (SmartOutputEvent.UPDATE_H, key_name, args)
        self.sequence.append(event)
    
    def update_v(self, key_name, *args):
        event = (SmartOutputEvent.UPDATE_V, key_name, args)
        self.sequence.append(event)

    def function(self, function_name, *args):
        event = (SmartOutputEvent.FUNCTION, function_name, args)
        self.sequence.append(event)

    def emit(self):
        if self.sequence:
            event = (self.sequence, self.source)
            self.mind.emit(self.topic, event)


class SmartOutputReflex(Reflex):
        
    def on_configure(self):

        self.userdisplay = None
        self.username = None
        self.userid = None
        self.functions = {}
        
        self.init_keys()
        self.preferences = self.init_preferences()
        self.update_functions(None)

        # Configure listeners
        self.add_listener(TOPIC_LOGIN_CHANGED, self.on_login_changed)
        self.add_listener(TOPIC_WINDOW_CHANGED, self.on_window_changed)
        self.add_listener(TOPIC_SMARTOUTPUT_EVENT, self.on_event)

    def on_event(self, topic_name, event):
        # self.log.debug(f"Reflex {self.name} for a new event, topic_name={topic_name}, event={event}")
        # self.log.debug(f"{self.__class__.__name__} is parsing a sequence")
        sequence, source = event

        for event_type, name, args in sequence:
            if event_type == SmartOutputEvent.FUNCTION:
                self.run_function(name, *args)
            elif event_type == SmartOutputEvent.UPDATE:
                # self.log.debug(f"{self.__class__.__name__} received an UPDATE")
                self.run_update(name, *args)
            elif event_type == SmartOutputEvent.UPDATE_H:
                # self.log.debug(f"{self.__class__.__name__} received an UPDATE_H")
                self.run_update_h(name, *args)
            elif event_type == SmartOutputEvent.UPDATE_V:
                # self.log.debug(f"{self.__class__.__name__} received an UPDATE_V")
                self.run_update_v(name, *args)
            else:
                self.log.warn(f"Invalid event type in SmartOutputEvent: {event_type}")
    
    def run_update(self, key_name, value):
        if hasattr(self, key_name):
            getattr(self, key_name).update(value)
    
    def run_update_h(self, key_name, value):
        if hasattr(self, key_name):
            getattr(self, key_name).update_h(value)
    
    def run_update_v(self, key_name, value):
        if hasattr(self, key_name):
            getattr(self, key_name).update_v(value)
    
    def run_function(self, function_name, *args):
        self.log.info("Inside run_function. Looking for", function_name)
        
        if not function_name in self.functions:
            self.log.error("Unknown function: %s", function_name)
            return
        
        function = self.functions[function_name]

        if isinstance(function, list):
            # log.info(f"Running function {function_name} as list of events")
            
            for f in function:
                self.log.info(f["type"])
                if f["type"] == "keyboard":
                    VirtualEvent = VirtualKeyboardEvent
                elif f["type"] == "mouse":
                    VirtualEvent = VirtualMouseEvent
                else:
                    self.log.error(f"Unknown function type: {f['type']}")
                    continue
                
                with VirtualEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                    for key in f["sequence"]:
                        self.log.info("key:", key)
                        if isinstance(key, (int, float)):
                            eb.sleep(key)
                        elif key.startswith("+"):
                            eb.press(key[1:])
                        elif key.startswith("-"):
                            eb.release(key[1:])
                        else:
                            eb.press(key)
                            eb.release(key)

        elif isinstance(function, str):
            if hasattr(self, function):
                getattr(self, function)(*args)
            else:
                self.log.error(f"Unknown function: {function}")

        else:
            # log.info(f"Running function {function_name} as instance method")
            function(*args)

    def init_keys(self):

        self.SCROLL_VOLUME  = DelayedKey("SCROLL_VOLUME",  lambda v: self.run_function("volume_up") if v else self.run_function("volume_down"), 200)
        self.SCROLL_TABS    = DelayedKey("SCROLL_TABS",    lambda v: self.run_function("next_tab") if v else self.run_function("previous_tab"), 500)
        self.SCROLL_WINDOWS = DelayedKey("SCROLL_WINDOWS", lambda v: self.run_function("next_window") if v else self.run_function("previous_window"), 500)
        self.SCROLL_ZOOM    = DelayedKey("SCROLL_ZOOM",    lambda v: self.run_function("zoom_in") if v else self.run_function("zoom_out"), 200)
        self.SCROLL_UNDO    = DelayedKey("SCROLL_UNDO",    lambda v: self.run_function("undo") if v else self.run_function("redo"), 200)

        self.SCROLL_VKEYS   = DelayedKey("SCROLL_VKEYS",   self.scroll_v_key, 200)
        self.SCROLL_HKEYS   = DelayedKey("SCROLL_HKEYS",   self.scroll_h_key, 200)
        self.SCROLL_H       = DelayedKey("SCROLL_H",       self.scroll_h_send_cmd, 200)
        self.SCROLL_V       = DelayedKey("SCROLL_V",       self.scroll_v_send_cmd, 200)

        self.SCROLL_MAXIMIZE_MININIMIZE_WINDOW = DelayedKey(
            "SCROLL_MAXIMIZE_MININIMIZE_WINDOW", 
            lambda x: self.run_function("maximize_window") if x else self.run_function("minimize_window"),
            400
        )

        self.SCROLL_PLACE_WINDOW_LEFT_RIGHT = DelayedKey(
            "SCROLL_PLACE_WINDOW_LEFT_RIGHT", 
            lambda x: self.run_function("place_window_right") if x else self.run_function("place_window_left"),
            400
        )

        self.DUAL_WINDOWS_TABS = LockableDelayedKey(
                "DUAL_WINDOWS_TABS", 
                lambda v: self.run_function("next_window") if v else self.run_function("previous_window"), 
                lambda v: self.run_function("next_tab") if v else self.run_function("previous_tab"),
                800) # lockable1
        
        self.DUAL_UNDO_VOLUME  = LockableDelayedKey(
                "DUAL_UNDO_VOLUME",  
                lambda v: self.run_function("redo") if v else self.run_function("undo"),
                lambda v: self.run_function("volume_up") if v else self.run_function("volume_down"), 
                500) # lockable2

        self.ADVERSARIAL_PLACEWINDOW_OR_MAXMINWINDOW = AdversarialDelayedKey(
            "ADVERSARIAL_PLACEWINDOW_OR_MAXMINWINDOW",
            lambda x: self.run_function("place_window_right") if x >= 0 else self.run_function("place_window_left"),
            lambda x: self.run_function("minimize_window") if x >= 0 else self.run_function("maximize_window"),
            250, self.log
        )
    
        self.ADVERSARIAL_SWITCH_APPS_OR_WINDOWS = AdversarialDelayedKey(
            "ADVERSARIAL_SWITCH_APPS_OR_WINDOWS",
            lambda x: self.run_function("next_app") if x >= 0 else self.run_function("previous_app"),
            lambda x: self.run_function("next_app_window") if x >= 0 else self.run_function("previous_app_window"),
            100, self.log
        )
    
    def on_login_changed(self, topic_name, event):
        import pwd
        self.username, self.userdisplay = (None, None) if len(event) == 0 else event[0]
        self.userid = None if self.username is None else pwd.getpwnam(self.username).pw_uid
        # log.info(f"Shadow {self.name} received a login changed event: username={self.username}, display={self.userdisplay}")

    def on_window_changed(self, topic_name, event):
        window_class, app_name, window_name = event
        # log.info(f"Reflex {self.name} received a window changed event: window_class={window_class}, app_name={app_name}, window_name={window_name}")
        self.update_functions(app_name)
    
    def update_functions(self, app_name):
        for intent_name, options in self.preferences.items():
            if app_name in options:
                callback = options[app_name]
                self.functions[intent_name] = callback

            elif "default" in options:
                callback = options["default"]
                self.functions[intent_name] = callback

            else:
                self.log.error("No default function for intent %s", intent_name)
    
    def init_preferences(self):
        raw_preferences = {
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
            "next_app": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTMETA", "+KEY_TAB", "-KEY_TAB"]}],
            },
            "previous_app": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTMETA", "+KEY_LEFTSHIFT", "+KEY_TAB", "-KEY_TAB", "-KEY_LEFTSHIFT"]}],
            },
            "next_app_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTMETA", "+KEY_GRAVE", "-KEY_GRAVE"]}],
            },
            "previous_app_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTMETA", "+KEY_LEFTSHIFT", "+KEY_GRAVE", "-KEY_GRAVE", "-KEY_LEFTSHIFT"]}],
            },
            "next_workspace": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTALT", "+KEY_RIGHT", "-KEY_RIGHT", "-KEY_LEFTALT", "-KEY_LEFTCTRL"]}],
            },
            "previous_workspace": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTALT", "+KEY_LEFT", "-KEY_LEFT", "-KEY_LEFTALT", "-KEY_LEFTCTRL"]}],
            },
            "move_window_to_next_workspace": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTALT", "+KEY_LEFTSHIFT", "+KEY_RIGHT", "-KEY_RIGHT", "-KEY_LEFTSHIFT", "-KEY_LEFTALT", "-KEY_LEFTCTRL"]}],
            },
            "move_window_to_previous_workspace": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTALT", "+KEY_LEFTSHIFT", "+KEY_LEFT", "-KEY_LEFT", "-KEY_LEFTSHIFT", "-KEY_LEFTALT", "-KEY_LEFTCTRL"]}],
            },
            "select_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["-KEY_LEFTALT", "-KEY_LEFTMETA"]}],
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

                ("code", "Code", "Terminator", "Org.gnome.Nautilus", "Apache NetBeans IDE 12.5", "Gimp-2.10"): [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_PAGEUP", "-KEY_PAGEUP", "-KEY_LEFTCTRL"]}],
                
                "Gedit": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTALT", "+KEY_PAGEUP", "-KEY_PAGEUP", "-KEY_LEFTALT", "-KEY_LEFTCTRL"]}],

                "Treesheets": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_V", "-KEY_V", "-KEY_LEFTALT", "+KEY_P", "-KEY_P"]}],

                "jetbrains-studio": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_LEFT", "-KEY_LEFT", "-KEY_LEFTALT"]}],
            },
            "previous_tab": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_TAB", "-KEY_TAB", "-KEY_LEFTCTRL"]}],

                ("code", "Code", "Terminator", "Org.gnome.Nautilus", "Apache NetBeans IDE 12.5", "Gimp-2.10"): [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_PAGEDOWN", "-KEY_PAGEDOWN", "-KEY_LEFTCTRL"]}],
                
                "Gedit": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTALT", "+KEY_PAGEDOWN", "-KEY_PAGEDOWN", "-KEY_LEFTALT", "-KEY_LEFTCTRL"]}],

                "Treesheets": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_V", "-KEY_V", "-KEY_LEFTALT", "+KEY_N", "-KEY_N"]}],

                "jetbrains-studio": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_RIGHT", "-KEY_RIGHT", "-KEY_LEFTALT"]}],
            },
            "close_tab": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_W", "-KEY_W", "-KEY_LEFTCTRL"]}],

                ("Terminator", "Gnome-terminal"): [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_W", "-KEY_W", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],
                
                "jetbrains-studio": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_F4", "-KEY_F4", "-KEY_LEFTCTRL"]}],
                
                "Inkscape": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_F4", "-KEY_F4", "-KEY_LEFTALT"]}],
            },
            "place_window_right": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTMETA", "+KEY_RIGHT", "-KEY_RIGHT", "-KEY_LEFTMETA", 0.1, "+KEY_ESC", "-KEY_ESC"]}],
            },
            "place_window_left": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTMETA", "+KEY_LEFT", "-KEY_LEFT", "-KEY_LEFTMETA", 0.1, "+KEY_ESC", "-KEY_ESC"]}],
            },
            "minimize_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTMETA", "+KEY_H", "-KEY_H", "-KEY_LEFTMETA"]}],
            },
            "maximize_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_F10", "-KEY_F10", "-KEY_LEFTALT"]}],
            },
            "close_window": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_F4", "-KEY_F4", "-KEY_LEFTALT"]}],
            },
            "navigate_back": {
                "default": [{
                    "type": "mouse",
                    "sequence": ["+BTN_SIDE", "-BTN_SIDE"]}],

                "Apache NetBeans IDE 12.5": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_LEFT", "-KEY_LEFT", "-KEY_LEFTALT"]}],
            },
            "navigate_forward": {
                "default": [{
                    "type": "mouse",
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

                ("Code", "Apache NetBeans IDE 12.5", "Dia", "Inkscape", "QtCreator", "Joplin", "Treesheets"): [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_N", "-KEY_N", "-KEY_LEFTCTRL"]}],

                "Terminator": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_T", "-KEY_T", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],
            },
            "copy": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_C", "-KEY_C", "-KEY_LEFTCTRL"]}],

                ("Terminator", "Gnome-terminal"): [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_C", "-KEY_C", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],
            },
            "cut": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_X", "-KEY_X", "-KEY_LEFTCTRL"]}],

                ("Terminator", "Gnome-terminal"): [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_X", "-KEY_X", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],
            },
            "paste": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_V", "-KEY_V", "-KEY_LEFTCTRL"]}],

                ("Terminator", "Gnome-terminal"): [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_V", "-KEY_V", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],
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

                ("firefox", "firefox-beta", "QtCreator"): [{
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

                ("Gnome-terminal", "Terminator"): [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_F", "-KEY_F", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"]}],

                "Apache NetBeans IDE 12.5": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTALT", "+KEY_LEFTSHIFT", "+KEY_O", "-KEY_O", "-KEY_LEFTSHIFT", "-KEY_LEFTALT"]}],
            },

            # "search_selection": {
            #     "default": self.search_selection_with_duckduckgo,

            #     ("firefox", "firefox-beta", "Google-chrome"): [
            #         {"type": "keyboard",
            #         "sequence": ["+KEY_LEFTALT"]},

            #         {"type": "mouse",
            #         "sequence": ["+BTN_RIGHT", "-BTN_RIGHT", 0.2]},

            #         {"type": "keyboard",
            #         "sequence": ["-KEY_LEFTALT", "+KEY_S", "+KEY_S"]}],
            # },
            "search_selection_with_duckduckgo": {
                "default": self.search_selection_with_duckduckgo,
            },
            "search_selection_with_google": {
                "default": self.search_selection_with_google,
            },
            "search_selection_with_bing": {
                "default": self.search_selection_with_bing,
            },
            "search_selection_with_brave": {
                "default": self.search_selection_with_brave,
            },
            "scroll_h": {
                "default": self.scroll_h_1,
                ("Dia", "Inkscape"): self.scroll_h_2,
                "Google-chrome": self.scroll_h_3,
                "Eog": self.scroll_h_4,
            },
            "scroll_v": {
                "default": self.scroll_v_1,
                ("Dia", "Inkscape"): self.scroll_v_2,
                "Google-chrome": self.scroll_v_3,
                "Eog": self.scroll_v_4,
            },
            "ctrl_c": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_C", "-KEY_C", "-KEY_LEFTCTRL"],
                }],
            },
            "ctrl_d": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTCTRL", "+KEY_D", "-KEY_D", "-KEY_LEFTCTRL"],
                }],
            },
            "lock": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTMETA", "+KEY_L", "-KEY_L", "-KEY_LEFTMETA"],
                }],
            },
            "logout": {
                "default": self.logout,
            },
            "reboot": {
                "default": self.reboot,
            },
            "poweroff": {
                "default": self.poweroff,
            },
            "focus_mode": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_F11", "-KEY_F11"],
                }],

                "Evince": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_F5", "-KEY_F5"]}],
            },
            "system_menu": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_LEFTMETA", "-KEY_LEFTMETA"],
                }],
            },
            "rename": {
                "default": [{
                    "type": "keyboard",
                    "sequence": ["+KEY_F2", "-KEY_F2"],
                }],
            },
            "show_macro_help": {
                "default": self.show_macro_help,
            }
        }

        # Convert list of names to single names

        preferences = {}
        
        for function_name, options in raw_preferences.items():
            preferences[function_name] = {}
            for app_name_or_list, events in options.items():
                if isinstance(app_name_or_list, tuple):
                    for app_name in app_name_or_list:
                        preferences[function_name][app_name] = events
                else:
                    preferences[function_name][app_name_or_list] = events
        
        return preferences
    

    ######################################################################################
    # Advanced functions not easily mapped to keys
    ######################################################################################

    def search_selection_with_duckduckgo(self):
        self._search_selection("firefox", "https://duckduckgo.com/?q=")

    def search_selection_with_google(self):
        self._search_selection("firefox", "http://www.google.com.br/search?q=")

    def search_selection_with_bing(self):
        self._search_selection("firefox", "https://www.bing.com/search?q=")

    def search_selection_with_brave(self):
        self._search_selection("firefox", "https://search.brave.com/search?q=")

    def search_selection_with_ecosia(self):
        self._search_selection("firefox", "https://www.ecosia.org/search?q=")

    def _search_selection(self, browser, search_engine):
        self.log.info(f"Running search selection with browser='{browser}' and engine='{search_engine}'")
        
        if self.username is None:
            self.log.error("Could not find a user session to open this search")
        
        cmd = "su %s -c 'xclip -selection primary -o -l 1 -d %s'" % (self.username, self.userdisplay)
        proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        selection = proc.stdout.read().decode('utf-8')
        query = re.sub('\s', '%20', selection)
        cmd = f"su {self.username} -c 'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{self.userid}/bus DISPLAY={self.userdisplay} {browser} {search_engine}{query} &'"
        Popen(shlex.split(cmd))

    def show_macro_help(self):
        self.log.info(f"Starting show macro help")
                
        if self.username is None:
            self.log.error("Could not find a user session to open this search")

        imgpath = os.path.join(os.path.abspath('.'), 'images', 'help_numpad_as_macro_kbd.png')
        cmd = f"su {self.username} -c 'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{self.userid}/bus DISPLAY={self.userdisplay} eog {imgpath} &'"
        Popen(shlex.split(cmd))

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
    
    def scroll_h_4(self, value):
        self.log.debug(f"on scroll_h_4, {value}")
        self.SCROLL_H.update(-value)
    
    def scroll_v_4(self, value):
        self.log.debug(f"on scroll_v_4, {value}")
        self.SCROLL_V.update(-value)

    def scroll_h_send_cmd(self, value):
        self.log.debug("on scroll_h_send_cmd")
        key = "KEY_PAGEUP" if value > 0 else "KEY_PAGEDOWN"
        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTCTRL")
            eb.press(key)
            eb.release(key)
            eb.release("KEY_LEFTCTRL")
    
    def scroll_v_send_cmd(self, value):
        self.log.debug("on scroll_v_send_cmd")
        key = "KEY_PAGEUP" if value > 0 else "KEY_PAGEDOWN"
        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press(key)
            eb.release(key)

    def scroll_h_key(self, value):
        key = "KEY_LEFT" if value else "KEY_RIGHT"
        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press(key)
            eb.release(key)
    
    def scroll_v_key(self, value):
        key = "KEY_UP" if value else "KEY_DOWN"
        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press(key)
            eb.release(key)
    
    def logout(self):
        self.log.debug(f"logout {self.username} {self.userdisplay} {self.userid}")
        self._session_quit('logout')
    
    def reboot(self):
        self.log.debug("reboot")
        self._session_quit('reboot')
    
    def poweroff(self):
        self.log.debug(f"poweroff")
        self._session_quit('power-off')
    
    def _session_quit(self, action):
        if self.username is None:
            self.log.error("Could not find a current user session to initiate the logout command")

        else:
            cmd = f"su {self.username} -c 'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{self.userid}/bus DISPLAY={self.userdisplay} gnome-session-quit --{action}'"
            Popen(shlex.split(cmd))
    

class SmartOutput(Shadow):
    def on_configure(self):
        super().on_configure()
        self.add_reflex(SmartOutputReflex, autostart=True)

