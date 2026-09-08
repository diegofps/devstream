
from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.smart_output import SmartOutputEvent

from keys import AdversarialDelayedKey
from evdev import ecodes as e
from reflex import Reflex
from shadow import Shadow

REQUIRED_DEVICES = [
    "Logitech USB Trackball"
]

SOURCE_LOGITECH_MARBLE = "Logitech Marble"


class BaseMarbleReflex(Reflex):

    def __init__(self, 
                IJ_size=100, IJ_axis_lockable=False, IJ_single_shot=True, 
                select_window_on_deactivate=False, **kwargs):
        
        super().__init__(**kwargs)

        self.clean = True
        self.select_window_on_deactivate = select_window_on_deactivate
        self.scroll_IJ = AdversarialDelayedKey("scroll_IJ", self.on_event_J, self.on_event_I, IJ_size, self.log, IJ_axis_lockable, IJ_single_shot)

    def on_event(self, topic_name, event):

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

    def on_move_rel_y(self, event):
        self.scroll_IJ.update_v(event.value*5)

    def on_move_rel_x(self, event):
        self.scroll_IJ.update_h(event.value*5)
    
    def on_event_I(self, value):
        pass

    def on_event_J(self, value):
        pass

    def on_activate(self, clean=True):
        self.log.debug(f"{self.name} is activating, clean={clean}")
        self.clean = clean

    def on_deactivate(self):
        super().on_deactivate()
        self.scroll_IJ.clear()
        if self.select_window_on_deactivate:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("select_window")


class Marble_N(BaseMarbleReflex): # N

    def on_left_click(self, event): # A
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.update("BTN_LEFT", event.value)
        
    def on_down_click(self, event): # B
        self.log.debug("N: on_down_click " + str(event.value))
        if event.value == 1: # +B
            self.shift_reflex("B")
    
    def on_up_click(self, event): # C
        if event.value == 1: # +C
            self.shift_reflex("C")

    def on_right_click(self, event): # D
        if event.value == 1: # +D
            self.shift_reflex("D")
    
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


class Marble_B(BaseMarbleReflex):

    def on_left_click(self, event): # A
        self.clean = False
        if event.value == 1:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.press("KEY_LEFTMETA")
        elif event.value == 0:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.release("KEY_LEFTMETA")

    def on_down_click(self, event): # B
        self.log.debug("B: on_down_click " + str(event.value))
        if event.value == 0:
            if self.clean:
                self.log.debug("Ended state B and emitting go_to_declaration, clean = true")
                with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                    eb.function("go_to_declaration")
            else:
                self.log.debug("Ended state B with clean = false")
            self.shift_reflex("N")
    
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
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.function("scroll_h", event.value)

    def on_move_rel_y(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
            eb.function("scroll_v", event.value)



class Marble_C(BaseMarbleReflex):

    def on_left_click(self, event): # A
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("search_selection_with_brave")

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
            
            self.shift_reflex("N")

    def on_right_click(self, event): # D
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                eb.function("new_tab")
    
    def on_event_I(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("undo" if value > 0 else "redo")

    def on_event_J(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("volume_up" if value > 0 else "volume_down")


class Marble_D(BaseMarbleReflex):

    def __init__(self, **kwargs):
        super().__init__(IJ_axis_lockable=True, IJ_single_shot=False, select_window_on_deactivate=True, **kwargs)
    
    def on_deactivate(self):
        super().on_deactivate()
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
    
    def on_right_click(self, event): # D
        if event.value == 0:
            if self.clean:
                with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MARBLE) as eb:
                    eb.press("BTN_MIDDLE")
                    eb.release("BTN_MIDDLE")
            self.shift_reflex("N")
    
    def on_event_I(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("next_window" if value > 0 else "previous_window")

    def on_event_J(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("next_tab" if value > 0 else "previous_tab")



class LogitechMarble(Shadow):
    def on_configure(self):
        super().on_configure(required_devices=REQUIRED_DEVICES, source_name=SOURCE_LOGITECH_MARBLE)
        self.add_reflex(Marble_N, autostart=True)
        self.add_reflex(Marble_B)
        self.add_reflex(Marble_C)
        self.add_reflex(Marble_D)
