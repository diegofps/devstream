from utils import BaseNode, debug, info, warn, error
from nodes.device_writer import OutputEvent
from evdev import ecodes as e


REQUIRED_DEVICES = [
    "Logitech MX Anywhere 2S"
]

TOPIC_DEVICE_MX2S = "DeviceReader:Logitech MX Anywhere 2S"
TOPIC_MX2S_STATE  = "MX2S:State"


class BaseMX2SNode(BaseNode):

    def __init__(self, core, name):
        super().__init__(core, name)
        core.register_listener(TOPIC_MX2S_STATE, self.on_state_changed)
        self.active = False

    def on_state_changed(self, topic_name, package):
        clean = True
        
        if package[-1] == '*':
            package = package[:-1]
            clean = False
        
        if self.name == package:
            self.core.register_listener(TOPIC_DEVICE_MX2S, self.on_event)
            self.clean = clean
            
            if not self.active:
                self.active = True
                self.on_activate()

            debug("Registering listener", type(self).__name__)
            
        else:
            if self.active:
                self.active = False
                self.on_deactivate()
            
            self.core.unregister_listener(TOPIC_DEVICE_MX2S, self.on_event)

            debug("Unregistering listener", type(self).__name__)

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

    def __init__(self, core):
        super().__init__(core, "MX2S_N")
    
    def on_left_click(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("BTN_LEFT", event.value)

    def on_middle_click(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("BTN_MIDDLE", event.value)
        
    def on_right_click(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("BTN_RIGHT", event.value)

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            debug("Pressing H from MX2S_N")
            self.core.emit(TOPIC_MX2S_STATE, "MX2S_H")
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            debug("Pressing G from MX2S_N")
            self.core.emit(TOPIC_MX2S_STATE, "MX2S_G")
    
    def on_scroll(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("WHEEL_V", event.value)
    
    def on_scroll_left_click(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("WHEEL_H", +120)
    
    def on_scroll_right_click(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("WHEEL_H", -120)
    
    def on_move_rel_x(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("REL_Y", event.value)


class MX2S_H(BaseMX2SNode): # Navigator

    def __init__(self, core):
        super().__init__(core, "MX2S_H")
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("BTN_LEFT")

        else:
            with OutputEvent(self.core) as eb:
                eb.release("BTN_LEFT")
                eb.release("KEY_LEFTCTRL")

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 0:
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_W")
                eb.release("KEY_W")
                eb.release("KEY_LEFTCTRL")
            
    def on_right_click(self, event): # C
        self.clean = False

        if event.value == 0:
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_LEFTSHIFT")
                eb.press("KEY_T")
                eb.release("KEY_T")
                eb.release("KEY_LEFTSHIFT")
                eb.release("KEY_LEFTCTRL")

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            debug("Releasing H from MX2S_H, clean is", self.clean)

            if self.clean:
                with OutputEvent(self.core) as eb:
                    eb.press("BTN_EXTRA")
                    eb.release("BTN_EXTRA")
            
            self.core.emit(TOPIC_MX2S_STATE, "MX2S_N")
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            debug("Pressing G from MX2S_H, clean is", self.clean)
            self.core.emit(TOPIC_MX2S_STATE, "MX2S_HG")
    
    def on_scroll(self, event): # E
        self.clean = False
        with OutputEvent(self.core) as eb:
            eb.update("SCROLL_TABS", event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False

        if event.value != 0:
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_EQUAL")

        else:
            with OutputEvent(self.core) as eb:
                eb.release("KEY_EQUAL")
                eb.release("KEY_LEFTCTRL")
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        
        if event.value != 0:
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_MINUS")
        
        else:
            with OutputEvent(self.core) as eb:
                eb.release("KEY_MINUS")
                eb.release("KEY_LEFTCTRL")
    
    def on_move_rel_x(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("REL_Y", event.value)


class MX2S_G(BaseMX2SNode): # System

    def __init__(self, core):
        super().__init__(core, "MX2S_G")
        self.clean = True
    
    def on_deactivate(self):
        with OutputEvent(self.core) as eb:
            eb.release("KEY_LEFTALT")
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_Z")
                eb.sleep(0.25)
                eb.release("KEY_Z")
                eb.release("KEY_LEFTCTRL")

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 1:
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTALT")
                eb.press("KEY_F4")
        
        elif event.value == 0:
            with OutputEvent(self.core) as eb:
                eb.release("KEY_F4")
                eb.release("KEY_LEFTALT")
        
    def on_right_click(self, event): # C
        self.clean = False
        
        if event.value != 0:
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_LEFTSHIFT")
                eb.press("KEY_Z")
        else:
            with OutputEvent(self.core) as eb:
                eb.release("KEY_Z")
                eb.release("KEY_LEFTSHIFT")
                eb.release("KEY_LEFTCTRL")

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            debug("Pressing H from MX2S_H, clean is", self.clean)
            self.core.emit(TOPIC_MX2S_STATE, "MX2S_HG")
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            debug("Releasing G from MX2S_G, clean is", self.clean)

            if self.clean:
                with OutputEvent(self.core) as eb:
                    eb.press("BTN_SIDE")
                    eb.release("BTN_SIDE")

            self.core.emit(TOPIC_MX2S_STATE, "MX2S_N")
    
    def on_scroll(self, event): # E
        self.clean = False
        with OutputEvent(self.core) as eb:
            eb.update("SCROLL_WINDOWS", event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
    
    def on_move_rel_x(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("REL_Y", event.value)


class MX2S_HG(BaseMX2SNode): # Multimedia

    def __init__(self, core):
        super().__init__(core, "MX2S_HG")
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        with OutputEvent(self.core) as eb:
            eb.update("KEY_PLAYPAUSE", event.value)

    def on_middle_click(self, event): # B
        self.clean = False
        with OutputEvent(self.core) as eb:
            eb.update("KEY_STOPCD", event.value)
        
    def on_right_click(self, event): # C
        self.clean = False
        with OutputEvent(self.core) as eb:
            eb.update("KEY_MUTE", event.value)

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            debug("Releasing H from MX2S_HG, clean is", self.clean)

            self.core.emit(TOPIC_MX2S_STATE, "MX2S_G*")

            with OutputEvent(self.core) as eb:
                if self.clean:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")

                eb.release("KEY_LEFTALT")
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            debug("Releasing G from MX2S_HG, clean is", self.clean)

            self.core.emit(TOPIC_MX2S_STATE, "MX2S_H*")

            with OutputEvent(self.core) as eb:
                if self.clean:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")
                
                eb.release("KEY_LEFTALT")
    
    def on_scroll(self, event): # E
        self.clean = False
        with OutputEvent(self.core) as eb:
            eb.update("SCROLL_VOLUME", event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False
        with OutputEvent(self.core) as eb:
            eb.update("KEY_NEXTSONG", event.value)
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        with OutputEvent(self.core) as eb:
            eb.update("KEY_PREVIOUSSONG", event.value)
    
    def on_move_rel_x(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with OutputEvent(self.core) as eb:
            eb.update("REL_Y", event.value)


def on_init(core):

    core.add_node("MX2S_N", MX2S_N(core))
    core.add_node("MX2S_G", MX2S_G(core))
    core.add_node("MX2S_H", MX2S_H(core))
    core.add_node("MX2S_HG", MX2S_HG(core))
    
    core.require_device(REQUIRED_DEVICES)
    core.emit(TOPIC_MX2S_STATE, "MX2S_N")

