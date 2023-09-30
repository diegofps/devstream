
from shadows.smart_output import SmartOutputEvent
from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent

from evdev import ecodes as e
from reflex import Reflex

import log


REQUIRED_DEVICES = [
    "Logitech USB Trackball"
]

TOPIC_DEVICE_MARBLE = "DeviceReader:Logitech USB Trackball"
TOPIC_MARBLE_STATE = "Marble:State"

SOURCE_LOGITECH_MARBLE = "Logitech Marble"

class BaseMarbleNode(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.configure_states(TOPIC_MARBLE_STATE, TOPIC_DEVICE_MARBLE)

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
        self.counter = 0
    
    def on_left_click(self, event): # A
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.update("BTN_LEFT", event.value)
        
    def on_down_click(self, event): # B
        log.debug("N: on_down_click " + str(event.value))
        if event.value == 1: # +B
            log.debug("\n\n\nN: Entering state B " + str(self.counter))
            self.counter += 1
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_B")
    
    def on_up_click(self, event): # C
        if event.value == 1: # +C
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_C")

    def on_right_click(self, event): # D
        if event.value == 1: # +D
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_D")
    
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            value = self.smooth(event.value, 1.0, 2.0, 1, 20)
            eb.update("REL_X", value)
        
    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            value = self.smooth(event.value, 1.0, 2.0, 1, 20)
            eb.update("REL_Y", value)
    
    def smooth(self, value, multiply1, multiply2, threshold1, threshold2):
        
        abs_value = abs(value)

        if abs_value < threshold1:
            return int(value * multiply1)

        elif abs_value > threshold2:
            return int(value * multiply2)

        elif threshold1 == threshold2:
            return value * (multiply1 + multiply2) / 2

        else:
            return int(value * ((abs_value - threshold1) / (threshold2 - threshold1) * (multiply2 - multiply1) + multiply1))


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
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.press("KEY_LEFTMETA")

        elif event.value == 0:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.release("KEY_LEFTMETA")

    def on_down_click(self, event): # B
        log.debug("B: on_down_click " + str(event.value))
        if event.value == 0:

            if self.clean:
                log.debug("Ended state B and emitting go_to_declaration, clean = true")
                with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                    eb.function("go_to_declaration")
            else:
                log.debug("Ended state B with clean = false")
            
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_N")
    
    def on_up_click(self, event): # C
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("navigate_back")

    def on_right_click(self, event): # D
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("navigate_forward")
    
    def on_move_rel_x(self, event):
        self.clean = False

        # log.debug("Moving x in state B " + str(event.value))
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.function("scroll_h", event.value)

    def on_move_rel_y(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.function("scroll_v", event.value)



class Marble_C(BaseMarbleNode):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("search_selection")

    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("reopen_tab")
    
    def on_up_click(self, event): # C

        if event.value == 0: # -C

            if self.clean:
                with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                    eb.press("BTN_RIGHT")
                    eb.release("BTN_RIGHT")
            
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.unlock("DUAL_UNDO_VOLUME")
            
            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_N")

    def on_right_click(self, event): # D
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("new_tab")
    
    def on_move_rel_x(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.update_h("DUAL_UNDO_VOLUME", event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.update_v("DUAL_UNDO_VOLUME", -event.value * 5)


class Marble_D(BaseMarbleNode):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_deactivate(self):
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.function("select_window")
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("close_tab")
    
    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("close_window")
    
    def on_up_click(self, event): # C
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("advanced_search")
    
        # if event.value == 0:
        #     os.system("su diego -c 'gnome-session-quit --power-off'")
    
    def on_right_click(self, event): # D
        if event.value == 0:

            if self.clean:
                with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                    eb.press("BTN_MIDDLE")
                    eb.release("BTN_MIDDLE")
            
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.unlock("DUAL_WINDOWS_TABS")

            self.mind.emit(TOPIC_MARBLE_STATE, "Marble_N")
    
    def on_move_rel_x(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.update_h("DUAL_WINDOWS_TABS", event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.update_v("DUAL_WINDOWS_TABS", -event.value * 5)


def on_load(shadow):

    Marble_N(shadow)
    Marble_B(shadow)
    Marble_C(shadow)
    Marble_D(shadow)

    shadow.require_device(REQUIRED_DEVICES)
    shadow.mind.emit(TOPIC_MARBLE_STATE, "Marble_N")

