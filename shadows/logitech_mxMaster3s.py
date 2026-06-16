from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.smart_output import SmartOutputEvent
from evdev import ecodes as e
from reflex import Reflex
from shadow import Shadow

import log

REQUIRED_DEVICES = [
    "Logitech MX Master 3S",
    "LogiOps Virtual Input"
]

TOPIC_DEVICE_MXMASTER3S    = [f"DeviceReader:{x}" for x in REQUIRED_DEVICES]
TOPIC_MXMASTER3S_STATE     = "MXMaster3S:State"
SOURCE_LOGITECH_MXMASTER3S = "Logi MX Master 3S"


class BaseMXMaster3SNode(Reflex):

    def on_configure(self):
        for x in REQUIRED_DEVICES:
            self.add_listener(f"DeviceReader:{x}", self.on_event)

    def on_event(self, device_name, event):
        # log.debug(f"event received from {device_name}: {event}")

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

            elif event.code == e.BTN_FORWARD:
                log.debug("BTN_FORWARD event")
                self.on_side_ground_click(event)
                
            elif event.code == e.KEY_A:
                log.debug("KEY_A event")
                # self.on_side_up_click(event)
                
            elif event.code == e.KEY_B:
                # log.debug("KEY_B event")
                self.on_middle_click(event)
                

        elif event.type == e.EV_REL:

            if event.code == e.REL_X:
                self.on_move_rel_x(event)

            elif event.code == e.REL_Y:
                self.on_move_rel_y(event)

            elif event.code == e.REL_WHEEL_HI_RES:
                self.on_scroll(event)

            elif event.code == e.REL_HWHEEL_HI_RES:
                event.value = -event.value
                self.on_scroll_h(event)

    def on_activate(self):
        log.debug(f"{self.__class__.__name__} is activating")
        pass

    def on_deactivate(self):
        log.debug(f"{self.__class__.__name__} is deactivating")
        pass


class MXMaster3S_N(BaseMXMaster3SNode): # Normal

    def __init__(self, name=None):
        super().__init__(name)
    
    def on_left_click(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("BTN_LEFT", event.value)

    def on_middle_click(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("BTN_MIDDLE", event.value)
        
    def on_right_click(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("BTN_RIGHT", event.value)

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_H", 50)
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_G", 50)
    
    def on_side_ground_click(self, event): # F
        if event.value == 1: # +F
            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_F", 50)
    
    def on_scroll(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("WHEEL_V", event.value)
    
    def on_scroll_h(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("WHEEL_H", event.value)
    
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("REL_Y", event.value)


class MXMaster3S_H(BaseMXMaster3SNode): # Navigator (H:side-up)

    def __init__(self, name=None):
        super().__init__(name)
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("go_to_declaration")

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("close_tab")
            
    def on_right_click(self, event): # C
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("reopen_tab")

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            log.debug("Releasing H from MXMaster3S_H, clean is", self.clean)

            if self.clean:
                with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                    eb.function("navigate_forward")
            
            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_N", 50)
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            log.debug("Pressing G from MXMaster3S_H, clean is", self.clean)
            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_HG", 50)
    
    def on_side_ground_click(self, event): # F
        pass

    def on_scroll(self, event): # E
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("SCROLL_TABS", event.value)
    
    def on_scroll_h(self, event):
        pass
        
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("REL_Y", event.value)


class MXMaster3S_G(BaseMXMaster3SNode): # System (G:side-down)

    def __init__(self, name=None):
        super().__init__(name)
        self.clean = True
    
    def on_deactivate(self):
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.function("select_window")
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("undo")

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("close_window")
        
    def on_right_click(self, event): # C
        self.clean = False
        
        if event.value != 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("redo")

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            log.debug("Pressing H from MXMaster3S_H, clean is", self.clean)
            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_HG", 50)
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            log.debug("Releasing G from MXMaster3S_G, clean is", self.clean)

            if self.clean:
                with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                    eb.function("navigate_back")

            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_N", 50)
    
    def on_side_ground_click(self, event): # F
        pass

    def on_scroll(self, event): # E
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("SCROLL_WINDOWS", event.value)
    
    def on_scroll_h(self, event):
        pass
        
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("REL_Y", event.value)


class MXMaster3S_HG(BaseMXMaster3SNode): # Multimedia

    def __init__(self, name=None):
        super().__init__(name)
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("KEY_PLAYPAUSE", event.value)

    def on_middle_click(self, event): # B
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("KEY_STOPCD", event.value)
        
    def on_right_click(self, event): # C
        self.clean = False
        with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("KEY_MUTE", event.value)

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            log.debug("Releasing H from MXMaster3S_HG, clean is", self.clean)

            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_G*", 50)

            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                if self.clean:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")

                eb.release("KEY_LEFTALT")
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            log.debug("Releasing G from MXMaster3S_HG, clean is", self.clean)

            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_H*", 50)

            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                if self.clean:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")
                
                eb.release("KEY_LEFTALT")
    
    def on_side_ground_click(self, event): # F
        pass
    
    def on_scroll(self, event): # E
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("SCROLL_VOLUME", event.value)
    
    def on_scroll_h(self, event):
        pass
        
    def on_move_rel_x(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.function("scroll_h", event.value * 1.50)

    def on_move_rel_y(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.function("scroll_v", event.value * 2.00)


class MXMaster3S_F(BaseMXMaster3SNode): # Editor

    def __init__(self, name=None):
        super().__init__(name)
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("copy")

    def on_middle_click(self, event): # B
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("cut")
        
    def on_right_click(self, event): # C
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("paste")

    def on_side_up_click(self, event): # H
        pass
    
    def on_side_down_click(self, event): # G
        pass
    
    def on_side_ground_click(self, event): # F
        if event.value == 0: # -F
            log.debug("Releasing F from MXMaster3S_F, clean is", self.clean)

            if self.clean:
                with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")

            self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_N", 50)
    
    def on_scroll(self, event): # E
        self.clean = False
        speed = 8
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("SCROLL_UNDO", -speed if event.value > 0 else speed)
    
    def on_scroll_h(self, event):
        pass

    def on_move_rel_x(self, event):
        pass

    def on_move_rel_y(self, event):
        pass


class LogitechMXMaster3S(Shadow):

    def on_configure(self):
        # TODO: Monitor logid's log and restart its service when you detect the 5 tries giving up failure
        # journalctl command: sudo journalctl --lines 1 -u logid
        # target line for regex: Jun 03 13:54:57 ncc2501 logid[3187]: [WARN] Failed to add device /dev/hidraw3 after 5 tries. Treating as failure.

        self.add_reflex(MXMaster3S_N())
        self.add_reflex(MXMaster3S_G())
        self.add_reflex(MXMaster3S_H())
        self.add_reflex(MXMaster3S_F())
        self.add_reflex(MXMaster3S_HG())
    
        self.require_device(REQUIRED_DEVICES)
        self.activate_reflex("MXMaster3S_N", 50)

# def on_load(shadow):

#     # TODO: Monitor logid's log and restart its service when you detect the 5 tries giving up failure
#     # journalctl command: sudo journalctl --lines 1 -u logid
#     # target line for regex: Jun 03 13:54:57 ncc2501 logid[3187]: [WARN] Failed to add device /dev/hidraw3 after 5 tries. Treating as failure.

#     MXMaster3S_N(shadow)
#     MXMaster3S_G(shadow)
#     MXMaster3S_H(shadow)
#     MXMaster3S_F(shadow)
#     MXMaster3S_HG(shadow)
    
#     self.require_device(REQUIRED_DEVICES)
#     self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_N", 50)

