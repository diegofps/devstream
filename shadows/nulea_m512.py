
from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.smart_output import SmartOutputEvent

from evdev import ecodes as e
from reflex import Reflex
from shadow import Shadow

import log


REQUIRED_DEVICES = [
    "Compx 2.4G Receiver Mouse",
    "Nulea BT5.0 "
]

SOURCE_NULEAM512 = "Nulea M512"


class BaseNuleaM512Reflex(Reflex):

    def on_configure(self):
        for x in REQUIRED_DEVICES:
            self.add_listener(f"DeviceReader:{x}", self.on_event)

    def on_event(self, topic_name, event):
        # log.debug("Processing Nulea M512 event: ", self.name, event)

        if event.type == e.EV_KEY:

            if event.code == e.BTN_LEFT:
                self.on_bottom_left_click(event)

            elif event.code == e.BTN_RIGHT:
                self.on_bottom_right_click(event)

            elif event.code == e.BTN_MIDDLE:
                self.on_top_left_click(event)

            elif event.code == e.BTN_SIDE:
                self.on_top_right_click(event)

        elif event.type == e.EV_REL:

            # Sphere rotates horizontally
            if event.code == e.REL_X:
                self.on_move_rel_x(event)

            # Sphere rotates vertically
            elif event.code == e.REL_Y:
                self.on_move_rel_y(event)
            
            elif event.code == e.REL_WHEEL_HI_RES:
                self.on_wheel_left(event)
            
            elif event.code == e.REL_HWHEEL_HI_RES:
                self.on_wheel_right(event)
            
            else:
                log.debug("This is a different rel event")
    
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
        

class NuleaM512_N(BaseNuleaM512Reflex):

    def on_configure(self):
        super().on_configure()
        self.selecting_window = True
        self.btn_middle = 0
        self.btn_right = 0
        self.btn_left = 0
        self.counter = 0
        
    def on_top_right_click(self, event): # menu
        if event.value == 1:
            if self.btn_left != 0 or self.btn_right != 0 or self.btn_middle != 0:
                return
            
            log.debug("\n\n\nN: Entering state ALT " + str(self.counter))
            self.counter += 1
            self.shift_reflex("NuleaM512_ALT")
    
    def on_top_left_click(self, event): # middle
        self.btn_middle = event.value

        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.update("BTN_MIDDLE", event.value)

    def on_bottom_right_click(self, event): # right
        self.btn_right = event.value

        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.update("BTN_RIGHT", event.value)
    
    def on_bottom_left_click(self, event): # left
        self.btn_left = event.value

        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.update("BTN_LEFT", event.value)
    
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            value = self.smooth(event.value, 0.2, 0.5, 1, 20)
            eb.update("REL_X", value)
        
    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_NULEAM512) as eb:
            value = self.smooth(event.value, 0.2, 0.5, 1, 20)
            eb.update("REL_Y", value)
    
    def on_wheel_left(self, event):
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            if event.value > 0:
                eb.function("next_tab", event.value)
            else:
                eb.function("previous_tab", event.value)
        
    def on_wheel_right(self, event):
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
    

class NuleaM512_ALT(BaseNuleaM512Reflex):

    def on_configure(self):
        super().on_configure()
        self.selecting_window = False
        self.clean = True
    
    def on_activate(self):
        super().on_activate()
        self.selecting_window = False
        self.clean = True
    
    def on_deactivate(self):
        super().on_deactivate()
        if self.selecting_window:
            self.selecting_window = False
            with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
                eb.function("select_window")

    def on_top_right_click(self, event): # B
        if event.value == 0:
            self.shift_reflex("NuleaM512_N")
    
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
        with VirtualKeyboardEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.update("KEY_PLAYPAUSE", event.value)
    
    def on_move_rel_x(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.function("scroll_h", event.value)

    def on_move_rel_y(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            eb.function("scroll_v", event.value)

    def on_wheel_left(self, event):
        self.selecting_window = True
        self.clean = False

        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            if event.value < 0:
                eb.function("next_window")
            else:
                eb.function("previous_window")
        
    def on_wheel_right(self, event):
        self.clean = False
        
        with SmartOutputEvent(self.mind, SOURCE_NULEAM512) as eb:
            if event.value > 0:
                eb.function("zoom_in", event.value)
            else:
                eb.function("zoom_out", event.value)
        

class NuleaM512(Shadow):
    def on_configure(self):
        self.require_device(REQUIRED_DEVICES)
        self.add_reflex(NuleaM512_N(autostart=True))
        self.add_reflex(NuleaM512_ALT())
