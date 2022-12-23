from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent

from evdev import ecodes as e
from reflex import Reflex

import log


REQUIRED_DEVICES = [
    "Logitech MX Anywhere 2S"
]


TOPIC_DEVICE_MX2S = "DeviceReader:Logitech MX Anywhere 2S"
TOPIC_MX2S_STATE  = "MX2S:State"

SOURCE_LOGITECH_MX2S = "Logitech MX2S"

class BaseMX2SNode(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.configure_states(TOPIC_MX2S_STATE, TOPIC_DEVICE_MX2S)

    def on_event(self, device_name, event):

        if event.type == e.EV_KEY:

            if event.code == e.BTN_LEFT:
                self.on_left_click(event)

            elif event.code == e.BTN_MIDDLE:
                self.on_middle_click(event)

            elif event.code == e.BTN_RIGHT:
                self.on_right_click(event)

            elif event.code == e.BTN_SIDE:
                self.on_side_down_click(event)

            elif event.code == e.BTN_EXTRA:
                self.on_side_up_click(event)

        elif event.type == e.EV_REL:

            if event.code == e.REL_X:
                self.on_move_rel_x(event)

            elif event.code == e.REL_Y:
                self.on_move_rel_y(event)

            elif event.code == e.REL_WHEEL_HI_RES:
                self.on_scroll(event)

            elif event.code == e.REL_HWHEEL_HI_RES:

                if event.value < 0:
                    event.value = 1
                    self.on_scroll_right_click(event)

                    event.value = 0
                    self.on_scroll_right_click(event)
                
                else:
                    event.value = 1
                    self.on_scroll_left_click(event)

                    event.value = 0
                    self.on_scroll_left_click(event)

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass


class MX2S_N(BaseMX2SNode): # Normal

    def __init__(self, shadow):
        super().__init__(shadow)
    
    def on_left_click(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("BTN_LEFT", event.value)

    def on_middle_click(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("BTN_MIDDLE", event.value)
        
    def on_right_click(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("BTN_RIGHT", event.value)

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            log.debug("Pressing H from MX2S_N")
            self.mind.emit(TOPIC_MX2S_STATE, "MX2S_H")
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            log.debug("Pressing G from MX2S_N")
            self.mind.emit(TOPIC_MX2S_STATE, "MX2S_G")
    
    def on_scroll(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("WHEEL_V", event.value)
    
    def on_scroll_left_click(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("WHEEL_H", +120)
    
    def on_scroll_right_click(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("WHEEL_H", -120)
    
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("REL_Y", event.value)


class MX2S_H(BaseMX2SNode): # Navigator

    def __init__(self, shadow):
        super().__init__(shadow)
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("BTN_LEFT")

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.release("BTN_LEFT")
                eb.release("KEY_LEFTCTRL")

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 0:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_W")
                eb.release("KEY_W")
                eb.release("KEY_LEFTCTRL")
            
    def on_right_click(self, event): # C
        self.clean = False

        if event.value == 0:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_LEFTSHIFT")
                eb.press("KEY_T")
                eb.release("KEY_T")
                eb.release("KEY_LEFTSHIFT")
                eb.release("KEY_LEFTCTRL")

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            log.debug("Releasing H from MX2S_H, clean is", self.clean)

            if self.clean:
                with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                    eb.press("BTN_EXTRA")
                    eb.release("BTN_EXTRA")
            
            self.mind.emit(TOPIC_MX2S_STATE, "MX2S_N")
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            log.debug("Pressing G from MX2S_H, clean is", self.clean)
            self.mind.emit(TOPIC_MX2S_STATE, "MX2S_HG")
    
    def on_scroll(self, event): # E
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("SCROLL_TABS", event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False

        if event.value != 0:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_EQUAL")

        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.release("KEY_EQUAL")
                eb.release("KEY_LEFTCTRL")
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        
        if event.value != 0:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_MINUS")
        
        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.release("KEY_MINUS")
                eb.release("KEY_LEFTCTRL")
    
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("REL_Y", event.value)


class MX2S_G(BaseMX2SNode): # System

    def __init__(self, shadow):
        super().__init__(shadow)
        self.clean = True
    
    def on_deactivate(self):
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.release("KEY_LEFTALT")
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_Z")
                eb.sleep(0.25)
                eb.release("KEY_Z")
                eb.release("KEY_LEFTCTRL")

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 1:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.press("KEY_LEFTALT")
                eb.press("KEY_F4")
        
        elif event.value == 0:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.release("KEY_F4")
                eb.release("KEY_LEFTALT")
        
    def on_right_click(self, event): # C
        self.clean = False
        
        if event.value != 0:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_LEFTSHIFT")
                eb.press("KEY_Z")
        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                eb.release("KEY_Z")
                eb.release("KEY_LEFTSHIFT")
                eb.release("KEY_LEFTCTRL")

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            log.debug("Pressing H from MX2S_H, clean is", self.clean)
            self.mind.emit(TOPIC_MX2S_STATE, "MX2S_HG")
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            log.debug("Releasing G from MX2S_G, clean is", self.clean)

            if self.clean:
                with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                    eb.press("BTN_SIDE")
                    eb.release("BTN_SIDE")

            self.mind.emit(TOPIC_MX2S_STATE, "MX2S_N")
    
    def on_scroll(self, event): # E
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("SCROLL_WINDOWS", event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
    
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("REL_Y", event.value)


class MX2S_HG(BaseMX2SNode): # Multimedia

    def __init__(self, shadow):
        super().__init__(shadow)
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("KEY_PLAYPAUSE", event.value)

    def on_middle_click(self, event): # B
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("KEY_STOPCD", event.value)
        
    def on_right_click(self, event): # C
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("KEY_MUTE", event.value)

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            log.debug("Releasing H from MX2S_HG, clean is", self.clean)

            self.mind.emit(TOPIC_MX2S_STATE, "MX2S_G*")

            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                if self.clean:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")

                eb.release("KEY_LEFTALT")
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            log.debug("Releasing G from MX2S_HG, clean is", self.clean)

            self.mind.emit(TOPIC_MX2S_STATE, "MX2S_H*")

            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
                if self.clean:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")
                
                eb.release("KEY_LEFTALT")
    
    def on_scroll(self, event): # E
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("SCROLL_VOLUME", event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("KEY_NEXTSONG", event.value)
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("KEY_PREVIOUSSONG", event.value)
    
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MX2S) as eb:
            eb.update("REL_Y", event.value)

def on_load(shadow):

    MX2S_N(shadow)
    MX2S_G(shadow)
    MX2S_H(shadow)
    MX2S_HG(shadow)
    
    shadow.require_device(REQUIRED_DEVICES)
    shadow.mind.emit(TOPIC_MX2S_STATE, "MX2S_N")

