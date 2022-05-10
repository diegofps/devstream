from utils import BaseState, BaseConsumer
from evdev import ecodes as e
import time


class StateN(BaseState): # Normal

    def __init__(self, consumer, context):
        super().__init__(context)
        self.consumer = consumer
    
    def on_left_click(self, event):
        self.c.BTN_LEFT.update(event.value)

    def on_middle_click(self, event):
        self.c.BTN_MIDDLE.update(event.value)
        
    def on_right_click(self, event):
        # Right
        self.c.BTN_RIGHT.update(event.value)

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            self.consumer.set_state(self.consumer.state_H)
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            self.consumer.set_state(self.consumer.state_G)
    
    def on_scroll(self, event):
        self.c.bt_wheel_v.update(event.value)
    
    def on_scroll_left_click(self, event):
        self.c.bt_wheel_h.update(+120)
    
    def on_scroll_right_click(self, event):
        self.c.bt_wheel_h.update(-120)
    
    def on_move_rel_x(self, event):
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.c.bt_rel_y.update(event.value)


class StateH(BaseState): # Navigator

    def __init__(self, consumer, context):
        super().__init__(context)
        self.consumer = consumer
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.c.KEY_LEFTCTRL.press()
            self.c.BTN_LEFT.press()

        else:
            self.c.BTN_LEFT.release()
            self.c.KEY_LEFTCTRL.release()

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 0:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_W.press()
            self.c.KEY_W.release()
            self.c.KEY_LEFTCTRL.release()
        
    def on_right_click(self, event): # C
        self.clean = False

        if event.value == 0:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_LEFTSHIFT.press()
            self.c.KEY_T.press()
            self.c.KEY_T.release()
            self.c.KEY_LEFTSHIFT.release()
            self.c.KEY_LEFTCTRL.release()

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H

            if self.clean:
                self.c.BTN_EXTRA.press()
                self.c.BTN_EXTRA.release()
            
            self.consumer.set_state(self.consumer.state_N)
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            self.consumer.set_state(self.consumer.state_HG)
    
    def on_scroll(self, event): # E
        self.clean = False
        self.c.key_tabs.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False

        if event.value != 0:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_EQUAL.press()

        else:
            self.c.KEY_EQUAL.release()
            self.c.KEY_LEFTCTRL.release()
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        
        if event.value != 0:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_MINUS.press()
        
        else:
            self.c.KEY_MINUS.release()
            self.c.KEY_LEFTCTRL.release()
    
    def on_move_rel_x(self, event):
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.c.bt_rel_y.update(event.value)


class StateG(BaseState): # System

    def __init__(self, consumer, context):
        super().__init__(context)
        self.consumer = consumer
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_Z.press()
            time.sleep(0.25)
            self.c.KEY_Z.release()
            self.c.KEY_LEFTCTRL.release()


    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 1:
            self.c.KEY_LEFTALT.press()
            self.c.KEY_F4.press()
        elif event.value == 0:
            self.c.KEY_F4.release()
            self.c.KEY_LEFTALT.release()
        
    def on_right_click(self, event): # C
        self.clean = False
        
        if event.value != 0:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_LEFTSHIFT.press()
            self.c.KEY_Z.press()
        else:
            self.c.KEY_Z.release()
            self.c.KEY_LEFTSHIFT.release()
            self.c.KEY_LEFTCTRL.release()

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            self.consumer.set_state(self.consumer.state_HG)
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G

            if self.clean:
                self.c.BTN_SIDE.press()
                self.c.BTN_SIDE.release()

            self.consumer.set_state(self.consumer.state_N)
    
    def on_scroll(self, event): # E
        self.clean = False
        self.c.key_windows.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
    
    def on_move_rel_x(self, event):
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.c.bt_rel_y.update(event.value)


class StateHG(BaseState): # Multimedia

    def __init__(self, consumer, context):
        super().__init__(context)
        self.consumer = consumer
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        self.c.KEY_PLAYPAUSE.update(event.value)

    def on_middle_click(self, event): # B
        self.clean = False
        self.c.KEY_STOPCD.update(event.value)
        
    def on_right_click(self, event): # C
        self.clean = False
        self.c.KEY_MUTE.update(event.value)

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            self.consumer.set_state(self.consumer.state_G)
            self.consumer.state_G.clean = False

            if self.clean:
                self.c.KEY_LEFTMETA.press()
                self.c.KEY_LEFTMETA.release()
            
            if self.c.alt_mode:
                self.c.alt_mode = False
                self.c.KEY_LEFTALT.release()
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            self.consumer.set_state(self.consumer.state_H)
            self.consumer.state_H.clean = False

            if self.clean:
                self.c.KEY_LEFTMETA.press()
                self.c.KEY_LEFTMETA.release()
            
            if self.c.alt_mode:
                self.c.alt_mode = False
                self.c.KEY_LEFTALT.release()
    
    def on_scroll(self, event): # E
        self.clean = False
        self.c.key_volume.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False
        self.c.KEY_NEXTSONG.update(event.value)
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        self.c.KEY_PREVIOUSSONG.update(event.value)
    
    def on_move_rel_x(self, event):
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.c.bt_rel_y.update(event.value)



FILTERS = ["Logitech MX Anywhere 2S"]


class Consumer(BaseConsumer):

    def __init__(self, context):
        super().__init__(context)

        self.state_N  = StateN(self, context)
        self.state_G  = StateG(self, context)
        self.state_H  = StateH(self, context)
        self.state_HG = StateHG(self, context)

        self.state    = self.state_N

    def on_event(self, event):

        if event.type == e.EV_KEY:

            if event.code == e.BTN_LEFT:
                self.state.on_left_click(event)

            elif event.code == e.BTN_MIDDLE:
                self.state.on_middle_click(event)

            elif event.code == e.BTN_RIGHT:
                self.state.on_right_click(event)

            elif event.code == e.BTN_SIDE:
                self.state.on_side_down_click(event)

            elif event.code == e.BTN_EXTRA:
                self.state.on_side_up_click(event)

        elif event.type == e.EV_REL:

            if event.code == e.REL_X:
                self.state.on_move_rel_x(event)

            elif event.code == e.REL_Y:
                self.state.on_move_rel_y(event)

            elif event.code == e.REL_WHEEL_HI_RES:
                self.state.on_scroll(event)

            elif event.code == e.REL_HWHEEL_HI_RES:

                if event.value < 0:
                    event.value = 1
                    self.state.on_scroll_right_click(event)

                    event.value = 0
                    self.state.on_scroll_right_click(event)
                
                else:
                    event.value = 1
                    self.state.on_scroll_left_click(event)

                    event.value = 0
                    self.state.on_scroll_left_click(event)
