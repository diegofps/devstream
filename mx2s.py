from utils import BaseConsumer
from evdev import ecodes as e
import time


TARGET_DEVICE = "Logitech MX Anywhere 2S"


class BaseMX2SConsumer(BaseConsumer):

    def __init__(self, core):
        super().__init__(core)

    def on_event(self, event):

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


class MX2S_N(BaseMX2SConsumer): # Normal

    def __init__(self, core):
        super().__init__(core)
    
    def on_left_click(self, event):
        self.core.out.BTN_LEFT.update(event.value)

    def on_middle_click(self, event):
        self.core.out.BTN_MIDDLE.update(event.value)
        
    def on_right_click(self, event):
        self.core.out.BTN_RIGHT.update(event.value)

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            self.core.set_consumer(TARGET_DEVICE, "MX2S_H")
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            self.core.set_consumer(TARGET_DEVICE, "MX2S_G")
    
    def on_scroll(self, event):
        self.core.out.bt_wheel_v.update(event.value)
    
    def on_scroll_left_click(self, event):
        self.core.out.bt_wheel_h.update(+120)
    
    def on_scroll_right_click(self, event):
        self.core.out.bt_wheel_h.update(-120)
    
    def on_move_rel_x(self, event):
        self.core.out.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.core.out.bt_rel_y.update(event.value)


class MX2S_H(BaseMX2SConsumer): # Navigator

    def __init__(self, core):
        super().__init__(core)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.BTN_LEFT.press()

        else:
            self.core.out.BTN_LEFT.release()
            self.core.out.KEY_LEFTCTRL.release()

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 0:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_W.press()
            self.core.out.KEY_W.release()
            self.core.out.KEY_LEFTCTRL.release()
        
    def on_right_click(self, event): # C
        self.clean = False

        if event.value == 0:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_LEFTSHIFT.press()
            self.core.out.KEY_T.press()
            self.core.out.KEY_T.release()
            self.core.out.KEY_LEFTSHIFT.release()
            self.core.out.KEY_LEFTCTRL.release()

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H

            if self.clean:
                self.core.out.BTN_EXTRA.press()
                self.core.out.BTN_EXTRA.release()
            
            self.core.set_consumer(TARGET_DEVICE, "MX2S_N")
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            self.core.set_consumer(TARGET_DEVICE, "MX2S_HG")
    
    def on_scroll(self, event): # E
        self.clean = False
        self.core.out.key_tabs.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False

        if event.value != 0:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_EQUAL.press()

        else:
            self.core.out.KEY_EQUAL.release()
            self.core.out.KEY_LEFTCTRL.release()
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        
        if event.value != 0:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_MINUS.press()
        
        else:
            self.core.out.KEY_MINUS.release()
            self.core.out.KEY_LEFTCTRL.release()
    
    def on_move_rel_x(self, event):
        self.core.out.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.core.out.bt_rel_y.update(event.value)


class MX2S_G(BaseMX2SConsumer): # System

    def __init__(self, core):
        super().__init__(core)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_Z.press()
            time.sleep(0.25)
            self.core.out.KEY_Z.release()
            self.core.out.KEY_LEFTCTRL.release()

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 1:
            self.core.out.KEY_LEFTALT.press()
            self.core.out.KEY_F4.press()
        elif event.value == 0:
            self.core.out.KEY_F4.release()
            self.core.out.KEY_LEFTALT.release()
        
    def on_right_click(self, event): # C
        self.clean = False
        
        if event.value != 0:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_LEFTSHIFT.press()
            self.core.out.KEY_Z.press()
        else:
            self.core.out.KEY_Z.release()
            self.core.out.KEY_LEFTSHIFT.release()
            self.core.out.KEY_LEFTCTRL.release()

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            self.core.set_consumer(TARGET_DEVICE, "MX2S_HG")
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G

            if self.clean:
                self.core.out.BTN_SIDE.press()
                self.core.out.BTN_SIDE.release()

            self.core.set_consumer(TARGET_DEVICE, "MX2S_N")
    
    def on_scroll(self, event): # E
        self.clean = False
        self.core.out.key_windows.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
    
    def on_move_rel_x(self, event):
        self.core.out.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.core.out.bt_rel_y.update(event.value)


class MX2S_HG(BaseMX2SConsumer): # Multimedia

    def __init__(self, core):
        super().__init__(core)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        self.core.out.KEY_PLAYPAUSE.update(event.value)

    def on_middle_click(self, event): # B
        self.clean = False
        self.core.out.KEY_STOPCD.update(event.value)
        
    def on_right_click(self, event): # C
        self.clean = False
        self.core.out.KEY_MUTE.update(event.value)

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            consumer = self.core.set_consumer(TARGET_DEVICE, "MX2S_G")
            consumer.clean = False

            if self.clean:
                self.core.out.KEY_LEFTMETA.press()
                self.core.out.KEY_LEFTMETA.release()
            
            self.core.out.KEY_LEFTALT.release()
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            consumer = self.core.set_consumer(TARGET_DEVICE, "MX2S_H")
            consumer.clean = False

            if self.clean:
                self.core.out.KEY_LEFTMETA.press()
                self.core.out.KEY_LEFTMETA.release()
            
            self.core.out.KEY_LEFTALT.release()
    
    def on_scroll(self, event): # E
        self.clean = False
        self.core.out.key_volume.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False
        self.core.out.KEY_NEXTSONG.update(event.value)
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        self.core.out.KEY_PREVIOUSSONG.update(event.value)
    
    def on_move_rel_x(self, event):
        self.core.out.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.core.out.bt_rel_y.update(event.value)


def on_init(core):

    core.consumers["MX2S_N"]  = MX2S_N(core)
    core.consumers["MX2S_G"]  = MX2S_G(core)
    core.consumers["MX2S_H"]  = MX2S_H(core)
    core.consumers["MX2S_HG"] = MX2S_HG(core)

    core.listeners[TARGET_DEVICE] = core.consumers["MX2S_N"]
