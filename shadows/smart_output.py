
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
    SLEEP = 2

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

        self.preferences = {
            "change_windows": {
                "default": self.change_windows_1,
            },
            "change_history": {
                "default": self.change_history_1,
            },
            "change_volume": {
                "default": self.change_volume_1,
            },
            "change_zoom": {
                "default": self.change_zoom_1,
            },
            "change_tabs": {
                "default": self.change_tabs_1,
                "Code": self.change_tabs_2,
                "Terminator": self.change_tabs_2,
                "Gedit": self.change_tabs_3,
                "Org.gnome.Nautilus": self.change_tabs_2,
                "Apache NetBeans IDE 12.5": self.change_tabs_2,
                "Treesheets": self.change_tabs_4, 
            },
            "close_tab": {
                "default": self.close_tab_1,
                "Terminator": self.close_tab_2,
                "Gnome-terminal": self.close_tab_2,
            },
            "close_window": {
                "default": self.close_window_1,
            },
            "navigate_back": {
                "default": self.navigate_back_1,
                "Apache NetBeans IDE 12.5": self.navigate_back_2
            },
            "navigate_forward": {
                "default": self.navigate_forward_1,
                "Apache NetBeans IDE 12.5": self.navigate_forward_2
            },
            "reopen_tab": {
                "default": self.reopen_tab_1,
            },
            "new_tab": {
                "default": self.new_tab_1,
                "Code": self.new_tab_2,
                "Apache NetBeans IDE 12.5": self.new_tab_2,
                "Terminator": self.new_tab_3,
                "Dia": self.new_tab_2,
                "Inkscape": self.new_tab_2,
                "QtCreator": self.new_tab_2,
                "Joplin": self.new_tab_2,
                "Treesheets": self.new_tab_2, 
            },
            "go_to_declaration": {
                "default": self.go_to_declaration_1,
            },
            "search_selection": {
                "default": self.search_selection_1,
                "firefox": self.search_selection_2,
                "firefox-beta": self.search_selection_2,
                "Google-chrome": self.search_selection_2,
            },
            "advanced_search": {
                "default": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_F", "-KEY_F", "-KEY_LEFTCTRL"],}],

                "jetbrains-studio": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_N", 0.1, "-KEY_N", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"],}],

                "Code": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_O", "-KEY_O", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"],}],

                "QtCreator": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_K", "-KEY_K", "-KEY_LEFTCTRL"],}],

                "Apache NetBeans IDE 12.5": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTALT", "+KEY_LEFTSHIFT", "+KEY_O", "-KEY_O", "-KEY_LEFTSHIFT", "-KEY_LEFTALT"],}],

                "Joplin": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_P", "-KEY_P", "-KEY_LEFTCTRL"],}],

                "Google-chrome": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_A", "-KEY_A", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"],}],

                "firefox": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_K", "-KEY_K", "-KEY_LEFTCTRL"],}],

                "firefox-beta": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_K", "-KEY_K", "-KEY_LEFTCTRL"],}],

                "Gedit": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_H", "-KEY_H", "-KEY_LEFTCTRL"],}],

                "Terminator": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_F", "-KEY_F", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"],}],

                "Gnome-terminal": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_LEFTSHIFT", "+KEY_F", "-KEY_F", "-KEY_LEFTSHIFT", "-KEY_LEFTCTRL"],}],
                
                "Org.gnome.Nautilus": [{
                        "type": "keyboard",
                        "sequence": ["+KEY_LEFTCTRL", "+KEY_F", "-KEY_F", "-KEY_LEFTCTRL"],}],
            },

            "scroll_h": {
                "default": self.scroll_h_1,
                "Dia": self.scroll_h_2,
                "Inkscape": self.scroll_h_2,
                "Google-chrome": self.scroll_h_3,
            },

            "scroll_v": {
                "default": self.scroll_v_1,
                "Dia": self.scroll_v_2,
                "Inkscape": self.scroll_v_2,
                "Google-chrome": self.scroll_v_3,
            },

        }

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
        self.SCROLL_UNDO    = DelayedKey("SCROLL_UNDO",    lambda v: self.run("navigate_back") if v else self.run("navigate_forward"), 200)

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
            
            # if function_name in self.functions:
            #     self.functions[function_name](*params)
            # else:
            #     log.error(f"Invalid function name ({function_name}) in {self.__class__.__name__} with params {params}")
        
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
        
    def change_history_1(self, value):
        if value:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_LEFTSHIFT")
                eb.press("KEY_Z")

                eb.release("KEY_Z")
                eb.release("KEY_LEFTSHIFT")
                eb.release("KEY_LEFTCTRL")
            
            # self.KEY_LEFTCTRL.press()
            # self.KEY_LEFTSHIFT.press()
            # self.KEY_Z.press()
            # self.KEY_Z.release()
            # self.KEY_LEFTSHIFT.release()
            # self.KEY_LEFTCTRL.release()

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_Z")

                eb.release("KEY_Z")
                eb.release("KEY_LEFTCTRL")
            
            # self.KEY_LEFTCTRL.press()
            # self.KEY_Z.press()
            # self.KEY_Z.release()
            # self.KEY_LEFTCTRL.release()
    
    def change_tabs_1(self, value):
        if value:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_LEFTSHIFT")
                eb.press("KEY_TAB")

                eb.release("KEY_TAB")
                eb.release("KEY_LEFTSHIFT")
                eb.release("KEY_LEFTCTRL")
            
            # self.KEY_LEFTCTRL.press()
            # self.KEY_LEFTSHIFT.press()
            # self.KEY_TAB.press()
            # self.KEY_TAB.release()
            # self.KEY_LEFTSHIFT.release()
            # self.KEY_LEFTCTRL.release()

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_TAB")

                eb.release("KEY_TAB")
                eb.release("KEY_LEFTCTRL")
            
            # self.KEY_LEFTCTRL.press()
            # self.KEY_TAB.press()
            # self.KEY_TAB.release()
            # self.KEY_LEFTCTRL.release()
    
    def change_tabs_2(self, value):
        if value:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_PAGEUP")

                eb.release("KEY_PAGEUP")
                eb.release("KEY_LEFTCTRL")
            # self.KEY_LEFTCTRL.press()
            # self.KEY_PAGEUP.press()
            # self.KEY_PAGEUP.release()
            # self.KEY_LEFTCTRL.release()

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_PAGEDOWN")

                eb.release("KEY_PAGEDOWN")
                eb.release("KEY_LEFTCTRL")
            
            # self.KEY_LEFTCTRL.press()
            # self.KEY_PAGEDOWN.press()
            # self.KEY_PAGEDOWN.release()
            # self.KEY_LEFTCTRL.release()
    
    def change_tabs_3(self, value):
        if value:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_LEFTALT")
                eb.press("KEY_PAGEUP")

                eb.release("KEY_PAGEUP")
                eb.release("KEY_LEFTALT")
                eb.release("KEY_LEFTCTRL")

            # self.KEY_LEFTCTRL.press()
            # self.KEY_LEFTALT.press()
            # self.KEY_PAGEUP.press()
            # self.KEY_PAGEUP.release()
            # self.KEY_LEFTALT.release()
            # self.KEY_LEFTCTRL.release()

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_LEFTALT")
                eb.press("KEY_PAGEDOWN")

                eb.release("KEY_PAGEDOWN")
                eb.release("KEY_LEFTALT")
                eb.release("KEY_LEFTCTRL")

            # self.KEY_LEFTCTRL.press()
            # self.KEY_LEFTALT.press()
            # self.KEY_PAGEDOWN.press()
            # self.KEY_PAGEDOWN.release()
            # self.KEY_LEFTALT.release()
            # self.KEY_LEFTCTRL.release()
    
    def change_tabs_4(self, value):
        
        # self.KEY_LEFTALT.press()
        # self.KEY_V.press()
        # self.KEY_V.release()
        # self.KEY_LEFTALT.release()
        # time.sleep(0.1)

        if value:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTALT")
                eb.press("KEY_V")
                eb.release("KEY_V")
                eb.release("KEY_LEFTALT")

                eb.press("KEY_P")
                eb.release("KEY_P")
                
            # self.KEY_P.press()
            # self.KEY_P.release()

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTALT")
                eb.press("KEY_V")
                eb.release("KEY_V")
                eb.release("KEY_LEFTALT")

                eb.press("KEY_N")
                eb.release("KEY_N")
            
            # self.KEY_N.press()
            # self.KEY_N.release()
    
    def change_windows_1(self, value):
        # self.KEY_LEFTALT.press()
        
        if value:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTALT")
                eb.release("KEY_TAB")
                eb.press("KEY_TAB")
                eb.release("KEY_TAB")
            
            # self.KEY_TAB.press()
            # self.KEY_TAB.release()

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTALT")
                eb.press("KEY_LEFTSHIFT")
                eb.press("KEY_TAB")
                eb.release("KEY_TAB")
                eb.release("KEY_LEFTSHIFT")
            
            # self.KEY_LEFTSHIFT.press()
            # self.KEY_TAB.press()
            # self.KEY_TAB.release()
            # self.KEY_LEFTSHIFT.release()
    
    def change_zoom_1(self, value):
        if value:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_EQUAL")
                eb.release("KEY_EQUAL")
                eb.release("KEY_LEFTCTRL")
            
            # self.KEY_LEFTCTRL.press()
            # self.KEY_EQUAL.press()
            # self.KEY_EQUAL.release()
            # self.KEY_LEFTCTRL.release()

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_MINUS")
                eb.release("KEY_MINUS")
                eb.release("KEY_LEFTCTRL")
            
            # self.KEY_LEFTCTRL.press()
            # self.KEY_MINUS.press()
            # self.KEY_MINUS.release()
            # self.KEY_LEFTCTRL.release()
    
    def change_volume_1(self, value):
        if value:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_VOLUMEUP")
                eb.release("KEY_VOLUMEUP")
            
            # self.KEY_VOLUMEUP.press()
            # self.KEY_VOLUMEUP.release()

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
                eb.press("KEY_VOLUMEDOWN")
                eb.release("KEY_VOLUMEDOWN")
            
            # self.KEY_VOLUMEDOWN.press()
            # self.KEY_VOLUMEDOWN.release()

    def close_tab_1(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTCTRL")
            eb.press("KEY_W")
            eb.release("KEY_W")
            eb.release("KEY_LEFTCTRL")

        # self.KEY_LEFTCTRL.press()
        # self.KEY_W.press()

        # self.KEY_W.release()
        # self.KEY_LEFTCTRL.release()
        
    def close_tab_2(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTCTRL")
            eb.press("KEY_LEFTSHIFT")
            eb.press("KEY_W")
            eb.release("KEY_W")
            eb.release("KEY_LEFTSHIFT")
            eb.release("KEY_LEFTCTRL")

        # self.KEY_LEFTCTRL.press()
        # self.KEY_LEFTSHIFT.press()
        # self.KEY_W.press()

        # self.KEY_W.release()
        # self.KEY_LEFTSHIFT.release()
        # self.KEY_LEFTCTRL.release()

    def close_window_1(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTALT")
            eb.press("KEY_F4")
            eb.release("KEY_F4")
            eb.release("KEY_LEFTALT")
        
        # self.KEY_LEFTALT.press()
        # self.KEY_F4.press()

        # self.KEY_F4.release()
        # self.KEY_LEFTALT.release()
        
    def navigate_back_1(self):

        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("BTN_SIDE")
            eb.release("BTN_SIDE")

        # self.BTN_SIDE.press()
        # self.BTN_SIDE.release()
        
    def navigate_back_2(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTALT")
            eb.press("KEY_LEFT")
            eb.release("KEY_LEFT")
            eb.release("KEY_LEFTALT")

        # self.KEY_LEFTALT.press()
        # self.KEY_LEFT.press()

        # self.KEY_LEFT.release()
        # self.KEY_LEFTALT.release()
    
    def navigate_forward_1(self):

        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("BTN_EXTRA")
            eb.release("BTN_EXTRA")
        
        # self.BTN_EXTRA.press()
        # self.BTN_EXTRA.release()
        
    def navigate_forward_2(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTALT")
            eb.press("KEY_RIGHT")
            eb.release("KEY_RIGHT")
            eb.release("KEY_LEFTALT")
        
        # self.KEY_LEFTALT.press()
        # self.KEY_RIGHT.press()

        # self.KEY_RIGHT.release()
        # self.KEY_LEFTALT.release()
    
    def reopen_tab_1(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTCTRL")
            eb.press("KEY_LEFTSHIFT")
            eb.press("KEY_T")
            eb.release("KEY_T")
            eb.release("KEY_LEFTSHIFT")
            eb.release("KEY_LEFTCTRL")
        
        # self.KEY_LEFTCTRL.press()
        # self.KEY_LEFTSHIFT.press()
        # self.KEY_T.press()
        
        # self.KEY_T.release()
        # self.KEY_LEFTSHIFT.release()
        # self.KEY_LEFTCTRL.release()
    
    def new_tab_1(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTCTRL")
            eb.press("KEY_T")
            eb.release("KEY_T")
            eb.release("KEY_LEFTCTRL")

        # self.KEY_LEFTCTRL.press()
        # self.KEY_T.press()
    
        # self.KEY_T.release()
        # self.KEY_LEFTCTRL.release()

    def new_tab_2(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTCTRL")
            eb.press("KEY_N")
            eb.release("KEY_N")
            eb.release("KEY_LEFTCTRL")

        # self.KEY_LEFTCTRL.press()
        # self.KEY_N.press()
    
        # self.KEY_N.release()
        # self.KEY_LEFTCTRL.release()

    def new_tab_3(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTCTRL")
            eb.press("KEY_LEFTSHIFT")
            eb.press("KEY_T")
            eb.release("KEY_T")
            eb.release("KEY_LEFTSHIFT")
            eb.release("KEY_LEFTCTRL")

        # self.KEY_LEFTCTRL.press()
        # self.KEY_LEFTSHIFT.press()
        # self.KEY_T.press()

        # self.KEY_T.release()
        # self.KEY_LEFTSHIFT.release()
        # self.KEY_LEFTCTRL.release()

    def go_to_declaration_1(self):

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTCTRL")

        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("BTN_LEFT")
            eb.sleep(0.25)

        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.release("BTN_LEFT")

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.release("KEY_LEFTCTRL")

        # self.KEY_LEFTCTRL.press()
        # self.BTN_LEFT.press()
        
        # time.sleep(0.25)

        # self.BTN_LEFT.release()
        # self.KEY_LEFTCTRL.release()
    
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

        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("KEY_LEFTALT")

        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.press("BTN_RIGHT")
            eb.release("BTN_RIGHT")
            eb.sleep(0.2)
        
        with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.release("KEY_LEFTALT")
            eb.press("KEY_S")
            eb.release("KEY_S")

        # self.KEY_LEFTALT.press()
        # self.BTN_RIGHT.press()
        # self.BTN_RIGHT.release()

        # time.sleep(0.2)

        # self.KEY_LEFTALT.release()
        # self.KEY_S.press()
        # self.KEY_S.release()
    
    # def advanced_search_1(self):
    #     with VirtualKeyboardEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
    #         eb.press("KEY_LEFTCTRL")
    #         eb.press("KEY_F")
    #         eb.release("KEY_F")
    #         eb.release("KEY_LEFTCTRL")
        
        # self.KEY_LEFTCTRL.press()
        # self.KEY_F.press()

        # self.KEY_F.release()
        # self.KEY_LEFTCTRL.release()

    def scroll_h_1(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_H", value * 20)
        # self.WHEEL_H.update(value * 20)
    
    def scroll_v_1(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_V", value * -10)
        # self.WHEEL_V.update(value * -10)
    
    def scroll_h_2(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_H", value * 5)
        # self.WHEEL_H.update(value * 5)
    
    def scroll_v_2(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_V", value * -5)
        # self.WHEEL_V.update(value * -5)
    
    def scroll_h_3(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_H", value * 10)
        # self.WHEEL_H.update(value * 10)
    
    def scroll_v_3(self, value):
        with VirtualMouseEvent(self.mind, SOURCE_SMART_OUTPUT) as eb:
            eb.update("WHEEL_V", value * -10)
        # self.WHEEL_V.update(value * -10)
    

def on_load(shadow):
    SmartOutput(shadow)

