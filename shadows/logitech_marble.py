from shadows.device_writer import OutputEvent
from evdev import ecodes as e
from reflex import Reflex

import log


REQUIRED_DEVICES = [
    "Logitech USB Trackball"
]

TOPIC_DEVICE_MARBLE = "DeviceReader:Logitech USB Trackball"
TOPIC_MARBLE_STATE = "Marble:State"


class BaseMarbleNode(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.active = False
        self.add_listener(TOPIC_MARBLE_STATE, self.on_state_changed)

    def on_state_changed(self, topic_name, event):
        clean = True
        
        if event[-1] == '*':
            event = event[:-1]
            clean = False
        
        if self.name == event:
            self.add_listener(TOPIC_DEVICE_MARBLE, self.on_event)
            self.clean = clean

            if not self.active:
                self.active = True
                self.on_activate()

        else:
            if self.active:
                self.active = False
                self.on_deactivate()
            
            self.remove_listener(TOPIC_DEVICE_MARBLE, self.on_event)

    def on_event(self, topic_name, event):
        # log.debug("Processing marble event", self.name, event)

        if event.type == e.EV_KEY:

            # big_left
            if event.code == e.BTN_LEFT:
                self.on_left_click(event)

            # small left
            elif event.code == e.BTN_SIDE:
                self.on_down_click(event)                    

            # small right
            elif event.code == e.BTN_EXTRA:
                self.on_up_click(event)

            # big right
            elif event.code == e.BTN_RIGHT:
                self.on_right_click(event)

        elif event.type == e.EV_REL:

            # Ball rotates horizontally
            if event.code == e.REL_X:
                self.on_move_rel_x(event)

            # Ball rotates vertically
            elif event.code == e.REL_Y:
                self.on_move_rel_y(event)
    
    def on_activate(self):
        pass

    def on_deactivate(self):
        pass


class Marble_N(BaseMarbleNode): # N

    def __init__(self, shadow):
        super().__init__(shadow)
    
    def on_left_click(self, event): # A
        with OutputEvent(self.mind) as eb:
            eb.update("BTN_LEFT", event.value)
        
    def on_down_click(self, event): # B
        if event.value == 1: # +B
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_B")
    
    def on_up_click(self, event): # C
        if event.value == 1: # +C
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_C")

    def on_right_click(self, event): # D
        if event.value == 1: # +D
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_D")
    
    def on_move_rel_x(self, event):
        with OutputEvent(self.mind) as eb:
            eb.update("REL_X", int(event.value * 1.5))
        
    def on_move_rel_y(self, event):
        with OutputEvent(self.mind) as eb:
            eb.update("REL_Y", int(event.value * 1.5))


class Marble_B(BaseMarbleNode):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.clean = True
    
    def on_activate(self):
        super().on_activate()
        self.clean = True
    
    def on_deactivate(self):
        super().on_deactivate()

    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            with OutputEvent(self.mind) as eb:
                eb.press("KEY_LEFTMETA")

        elif event.value == 0:
            with OutputEvent(self.mind) as eb:
                eb.release("KEY_LEFTMETA")

    def on_down_click(self, event): # B
        if event.value == 0:

            if self.clean:
                with OutputEvent(self.mind) as eb:
                    eb.function("go_to_declaration")
            
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_N")
    
    def on_up_click(self, event): # C
        self.clean = False

        if event.value == 0:
            with OutputEvent(self.mind) as eb:
                eb.function("navigate_back")

    def on_right_click(self, event): # D
        self.clean = False

        if event.value == 0:
            with OutputEvent(self.mind) as eb:
                eb.function("navigate_forward")
    
    def on_move_rel_x(self, event):
        self.clean = False
        with OutputEvent(self.mind) as eb:
            eb.update("WHEEL_H", event.value * 20)

    def on_move_rel_y(self, event):
        self.clean = False
        with OutputEvent(self.mind) as eb:
            eb.update("WHEEL_V", -event.value * 10)



class Marble_C(BaseMarbleNode):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        
        if event.value == 0:
            with OutputEvent(self.mind) as eb:
                eb.function("search_selection")

    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 0:
            with OutputEvent(self.mind) as eb:
                eb.function("reopen_tab")
    
    def on_up_click(self, event): # C

        if event.value == 0: # -C

            with OutputEvent(self.mind) as eb:
                if self.clean:
                    eb.press("BTN_RIGHT")
                    eb.release("BTN_RIGHT")
            
                eb.unlock("DUAL_UNDO_VOLUME")
            
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_N")

    def on_right_click(self, event): # D
        self.clean = False

        if event.value == 0:
            with OutputEvent(self.mind) as eb:
                eb.function("new_tab")
    
    def on_move_rel_x(self, event):
        self.clean = False
        with OutputEvent(self.mind) as eb:
            eb.update_h("DUAL_UNDO_VOLUME", event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        with OutputEvent(self.mind) as eb:
            eb.update_v("DUAL_UNDO_VOLUME", -event.value * 5)


class Marble_D(BaseMarbleNode):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_deactivate(self):
        with OutputEvent(self.mind) as eb:
            eb.release("KEY_LEFTALT")
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 0:
            with OutputEvent(self.mind) as eb:
                eb.function("close_tab")
    
    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 0:
            with OutputEvent(self.mind) as eb:
                eb.function("close_window")
    
    def on_up_click(self, event): # C
        self.clean = False

        if event.value == 0:
            with OutputEvent(self.mind) as eb:
                eb.function("advanced_search")
    
        # if event.value == 0:
        #     os.system("su diego -c 'gnome-session-quit --power-off'")
    
    def on_right_click(self, event): # D
        if event.value == 0:

            with OutputEvent(self.mind) as eb:
                if self.clean:
                    eb.press("BTN_MIDDLE")
                    eb.release("BTN_MIDDLE")
            
                eb.unlock("DUAL_WINDOWS_TABS")

            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_N")
    
    def on_move_rel_x(self, event):
        self.clean = False
        with OutputEvent(self.mind) as eb:
            eb.update_h("DUAL_WINDOWS_TABS", event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        with OutputEvent(self.mind) as eb:
            eb.update_v("DUAL_WINDOWS_TABS", -event.value * 5)


def on_load(shadow):

    Marble_N(shadow)
    Marble_B(shadow)
    Marble_C(shadow)
    Marble_D(shadow)

    shadow.require_device(REQUIRED_DEVICES)
    shadow.mind.emit(TOPIC_MARBLE_STATE, "Marble_N")

