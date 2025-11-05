
from shadows.smart_output import SmartOutputEvent
from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent

from evdev import ecodes as e
from reflex import Reflex

import log


REQUIRED_DEVICES = [
    "Compx 2.4G Receiver Mouse"
]

TOPIC_DEVICE_NULEAM512 = "DeviceReader:Compx 2.4G Receiver Mouse"
TOPIC_NULEAM512_STATE = "NuleaM512:State"

SOURCE_NULEAM512 = "Nulea M512"

class BaseNuleaM512Node(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.configure_states(TOPIC_NULEAM512_STATE, TOPIC_DEVICE_NULEAM512)

    def on_event(self, topic_name, event):
        log.debug("Processing nuleam512 event", self.name, event)

        if event.type == e.EV_KEY:

            # bottom_left
            if event.code == e.BTN_LEFT:
                self.on_bottom_left_click(event)

            # bottom_right
            elif event.code == e.BTN_RIGHT:
                self.on_bottom_right_click(event)

            # top_left
            elif event.code == e.BTN_MIDDLE:
                self.on_top_left_click(event)

            # top_right
            elif event.code == e.BTN_SIDE:
                self.on_top_right_click(event)

        elif event.type == e.EV_REL:

            # Ball rotates horizontally
            if event.code == e.REL_X:
                self.on_move_rel_x(event)

            # Ball rotates vertically
            elif event.code == e.REL_Y:
                self.on_move_rel_y(event)
            
            elif event.code == e.REL_WHEEL_HI_RES:
                self.on_wheel_left(event)
            
            elif event.code == e.REL_HWHEEL_HI_RES:
                self.on_wheel_right(event)
            
            else:
                log.debug("This is a different rel event")
        
        else:
            log.debug("This event is not KEY nor REL")
    
    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_top_left_click(self, event):
        log.debug("B: on_top_left_click " + str(event.value))
        
    def on_top_right_click(self, event):
        log.debug("B: on_top_right_click " + str(event.value))
        
    def on_bottom_left_click(self, event):
        log.debug("B: on_bottom_left_click " + str(event.value))
        
    def on_bottom_right_click(self, event):
        log.debug("B: on_bottom_right_click " + str(event.value))
        
    def on_move_rel_x(self, event):
        log.debug("B: on_move_rel_x " + str(event.value))
        
    def on_move_rel_y(self, event):
        log.debug("B: on_move_rel_y " + str(event.value))
        
    def on_wheel_left(self, event):
        log.debug("B: on_wheel_left " + str(event.value))
        
    def on_wheel_right(self, event):
        log.debug("B: on_wheel_right " + str(event.value))
        

class NuleaM512_N(BaseNuleaM512Node):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.selecting_window = True
        self.btn_middle = 0
        self.btn_right = 0
        self.btn_left = 0
        self.counter = 0
        
    def on_top_right_click(self, event): # menu
        log.debug("N: on_top_right_click " + str(event.value))
        self.finish_window_selection()

        if event.value == 1:
            if self.btn_left != 0 or self.btn_right != 0 or self.btn_middle != 0:

                # Ignore enter menu when buttons are pressed
                return
                
                # log.debug("\n\n\nN: Releasing pressed buttons to enter menu")
                # with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
                #     if self.btn_left != 0:
                #         eb.update("BTN_LEFT", 0)
                #     if self.btn_middle != 0:
                #         eb.update("BTN_MIDDLE", 0)
                #     if self.btn_right != 0:
                #         eb.update("BTN_RIGHT", 0)
            
            log.debug("\n\n\nN: Entering state ALT " + str(self.counter))
            self.counter += 1
            self.mind.emit(TOPIC_NULEAM512_STATE, "NuleaM512_ALT", 50)
    
    def on_top_left_click(self, event): # middle
        log.debug("N: on_top_left_click " + str(event.value))
        self.finish_window_selection()
        self.btn_middle = event.value

        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.update("BTN_MIDDLE", event.value)

    def on_bottom_right_click(self, event): # right
        log.debug("N: on_bottom_right_click " + str(event.value))
        self.finish_window_selection()
        self.btn_right = event.value

        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.update("BTN_RIGHT", event.value)
    
    def on_bottom_left_click(self, event): # left
        log.debug("N: on_bottom_left_click " + str(event.value))
        self.finish_window_selection()
        self.btn_left = event.value

        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.update("BTN_LEFT", event.value)
    
    def on_move_rel_x(self, event):
        log.debug("N: on_move_rel_x " + str(event.value))
        self.finish_window_selection()

        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            value = self.smooth(event.value, 0.2, 0.5, 1, 20)
            eb.update("REL_X", value)
        
    def on_move_rel_y(self, event):
        log.debug("N: on_move_rel_y " + str(event.value))
        self.finish_window_selection()

        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            value = self.smooth(event.value, 0.2, 0.5, 1, 20)
            eb.update("REL_Y", value)
    
    def on_wheel_left(self, event):
        log.debug("N: on_wheel_left " + str(event.value))
        
        self.selecting_window = True
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.update("SCROLL_WINDOWS", -event.value)
        
    def on_wheel_right(self, event):
        log.debug("N: on_wheel_right " + str(event.value))
        self.finish_window_selection()
        
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.update("SCROLL_VOLUME", event.value)
        
    def smooth(self, value, multiply1, multiply2, threshold1, threshold2):
        
        abs_value = abs(value)

        if abs_value < threshold1:
            return value * multiply1

        elif abs_value > threshold2:
            return value * multiply2

        elif threshold1 == threshold2:
            return value * (multiply1 + multiply2) / 2

        else:
            return value * ((abs_value - threshold1) / (threshold2 - threshold1) * (multiply2 - multiply1) + multiply1)

    def finish_window_selection(self):
        if self.selecting_window:
            self.selecting_window = False
            with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
                eb.function("select_window")
    

class NuleaM512_ALT(BaseNuleaM512Node):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.clean = True
    
    def on_activate(self):
        super().on_activate()
        self.clean = True
    
    def on_deactivate(self):
        super().on_deactivate()

    def on_top_right_click(self, event): # B
        log.debug("B: on_down_click " + str(event.value))
        if event.value == 0:

            if self.clean:
                log.debug("Ended state B and emitting go_to_declaration, clean = true")
                with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
                    eb.function("navigate_back")
            else:
                log.debug("Ended state ALT with clean = false")
            
            self.mind.emit(TOPIC_NULEAM512_STATE, "NuleaM512_N", 50)
    
    def on_top_left_click(self, event):
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
                eb.function("close_window")
    
    def on_bottom_left_click(self, event): # C
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
                eb.function("close_tab")

    def on_bottom_right_click(self, event): # D
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
                eb.function("navigate_forward")
    
    def on_move_rel_x(self, event):
        self.clean = False

        # log.debug("Moving x in state B " + str(event.value))
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.function("scroll_h", event.value)

    def on_move_rel_y(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.function("scroll_v", event.value)

    def on_wheel_left(self, event):
        self.clean = False
        
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            if event.value > 0:
                eb.function("next_tab", event.value)
            else:
                eb.function("previous_tab", event.value)
        
    def on_wheel_right(self, event):
        self.clean = False
        
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            if event.value > 0:
                eb.function("zoom_in", event.value)
            else:
                eb.function("zoom_out", event.value)
        


def on_load(shadow):

    NuleaM512_N(shadow)
    NuleaM512_ALT(shadow)

    shadow.require_device(REQUIRED_DEVICES)
    shadow.mind.emit(TOPIC_NULEAM512_STATE, "NuleaM512_N", 50)

