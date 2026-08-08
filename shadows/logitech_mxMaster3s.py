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

SOURCE_LOGITECH_MXMASTER3S = "Logi MX Master 3S"


class MXMaster3S_LogidMonitor(Reflex):

    def on_configure(self):
        self.require_daemon()
    
    def run(self, daemon):
        log.debug(f"Starting LogidMonitor daemon thread")

        from subprocess import Popen, PIPE
        import shlex
        import time
        import os

        while not daemon.done:
            try:
                cmd = shlex.split("journalctl --lines 1 -u logid")

                with Popen(cmd, stdout=PIPE) as proc:
                    lines = proc.stdout.readlines()

                if lines and lines[0].decode('utf-8').endswith('after 5 tries. Treating as failure.\n'):
                    log.info('Detected logid is in a failure state, restarting the service')
                    os.system('service logid restart')
                
            except Exception as e:
                log.error(f"Failed to monitor logid service: {e}")
            
            time.sleep(3)
        
        log.debug(f"Ending LogidMonitor daemon thread")


class BaseMXMaster3SNode(Reflex):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean = True
    
    def on_configure(self):
        for x in REQUIRED_DEVICES:
            self.add_listener(f"DeviceReader:{x}", self.on_event)

    def on_event(self, device_name, event):
        # log.debug(f"Event received from {device_name}: {event}")

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

    def on_activate(self, clean=True):
        log.debug(f"{self.name} is activating, clean={clean}")
        self.clean = clean

    def on_deactivate(self):
        log.debug(f"{self.name} is deactivating")


class MXMaster3S_N(BaseMXMaster3SNode): # Normal

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
            self.shift_reflex("MXMaster3S_H")
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            self.shift_reflex("MXMaster3S_G")
            # self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_G", 50)
    
    def on_side_ground_click(self, event): # F
        if event.value == 1: # +F
            self.shift_reflex("MXMaster3S_F")
    
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
            
            self.shift_reflex("MXMaster3S_N")
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            log.debug("Pressing G from MXMaster3S_H, clean is", self.clean)
            self.shift_reflex("MXMaster3S_HG")
    
    def on_side_ground_click(self, event): # D
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

    def on_deactivate(self):
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.function("select_window")
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                # eb.function("undo")
                eb.function("previous_workspace")

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("close_window")
        
    def on_right_click(self, event): # C
        self.clean = False
        
        if event.value != 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                # eb.function("redo")
                eb.function("next_workspace")

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            log.debug("Pressing H from MXMaster3S_H, clean is", self.clean)
            self.shift_reflex("MXMaster3S_HG")
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            log.debug("Releasing G from MXMaster3S_G, clean is", self.clean)

            if self.clean:
                with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                    eb.function("navigate_back")
            
            self.shift_reflex("MXMaster3S_N")
    
    def on_side_ground_click(self, event): # D
        pass

    def on_scroll(self, event): # E
        self.clean = False
        with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("SCROLL_WINDOWS", event.value)
    
    def on_scroll_h(self, event): # F
        pass
        
    def on_move_rel_x(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("REL_X", event.value)

    def on_move_rel_y(self, event):
        with VirtualMouseEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
            eb.update("REL_Y", event.value)


class MXMaster3S_HG(BaseMXMaster3SNode): # Multimedia
    
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

            self.shift_reflex("MXMaster3S_G", clean=False)
            # self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_G*", 50) # * means a non clean state

            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                if self.clean:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")

                eb.release("KEY_LEFTALT")
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            log.debug("Releasing G from MXMaster3S_HG, clean is", self.clean)

            self.shift_reflex("MXMaster3S_H", clean=False)
            # self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_H*", 50)

            with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                if self.clean:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")
                
                eb.release("KEY_LEFTALT")
    
    def on_side_ground_click(self, event): # D
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


class MXMaster3S_D(BaseMXMaster3SNode): # System
    
    def on_left_click(self, event): # A
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("ctrl_c")

    def on_middle_click(self, event): # B
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("lock")
        
    def on_right_click(self, event): # C
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("ctrl_d")

    def on_side_up_click(self, event): # H
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("reboot")
    
    def on_side_down_click(self, event): # G
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                eb.function("poweroff")
    
    def on_side_ground_click(self, event): # D
        if event.value == 0: # -F
            log.debug("Releasing F from MXMaster3S_F, clean is", self.clean)

            if self.clean:
                with VirtualKeyboardEvent(self.mind, SOURCE_LOGITECH_MXMASTER3S) as eb:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")

            self.shift_reflex("MXMaster3S_N")
            # self.mind.emit(TOPIC_MXMASTER3S_STATE, "MXMaster3S_N", 50)
    
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
        self.add_reflex(MXMaster3S_LogidMonitor(keepalive=True))
        self.add_reflex(MXMaster3S_N(autostart=True))
        self.add_reflex(MXMaster3S_H())
        self.add_reflex(MXMaster3S_G())
        self.add_reflex(MXMaster3S_HG())
        self.add_reflex(MXMaster3S_D())
        self.require_device(REQUIRED_DEVICES)

