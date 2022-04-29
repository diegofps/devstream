from utils import smooth, BaseState
import time

class StateN(BaseState): # N

    def __init__(self, context):
        super().__init__(context)
        self.c = context
    
    def on_left_click(self, event): # A
        self.c.bt_left.update(event.value)

    def on_down_click(self, event): # B
        if event.value == 1: # +B
            self.c.set_state(self.c.state_B)
    
    def on_up_click(self, event): # C
        if event.value == 1: # +C
            self.c.set_state(self.c.state_C)

    def on_right_click(self, event): # D
        if event.value == 1: # +D
            self.c.set_state(self.c.state_D)
    
    def on_move_rel_x(self, event):
        self.c.bt_rel_x.update(smooth(event.value))

    def on_move_rel_y(self, event):
        self.c.bt_rel_y.update(smooth(event.value))


class StateB(BaseState):

    def __init__(self, context):
        super().__init__(context)
        self.c = context
        self.clean = True
    
    def on_activate(self):
        super().on_activate()
        self.clean = True
    
    def on_deactivate(self):
        super().on_deactivate()

    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.c.key_leftmeta.press()

        elif event.value == 0:
            self.c.key_leftmeta.release()

    def on_down_click(self, event): # B
        if event.value == 0:

            if self.clean:
                self.c.key_leftctrl.press()
                self.c.bt_left.press()
                time.sleep(0.25)
                self.c.bt_left.release()
                self.c.key_leftctrl.release()
            
            self.c.set_state(self.c.state_N)
    
    def on_up_click(self, event): # C
        self.clean = False
        self.c.key_back.update(event.value)

    def on_right_click(self, event): # D
        self.clean = False
        self.c.key_forward.update(event.value)
    
    def on_move_rel_x(self, event):
        self.clean = False
        self.c.bt_wheel_h.update(event.value * 20)

    def on_move_rel_y(self, event):
        self.clean = False
        self.c.bt_wheel_v.update(-event.value * 10)

class StateC(BaseState):

    def __init__(self, context):
        super().__init__(context)
        self.c = context
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.c.key_play_pause.press()
        
        elif event.value == 0:
            self.c.key_play_pause.release()

    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 1:
            self.c.key_mute_unmute.press()
        
        elif event.value == 0:
            self.c.key_mute_unmute.release()
    
    def on_up_click(self, event): # C

        if event.value == 0: # -C

            if self.clean:
                self.c.bt_right.press()
                self.c.bt_right.release()
            
            self.c.lockable2.unlock()
            self.c.set_state(self.c.state_N)

    def on_right_click(self, event): # D
        self.clean = False

        if event.value == 1:
            self.c.key_leftctrl.press()
            self.c.key_c.press()
        
        elif event.value == 0:
            self.c.key_c.release()
            self.c.key_leftctrl.release()
    
    def on_move_rel_x(self, event):
        self.clean = False
        self.c.lockable2.update_h(event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        self.c.lockable2.update_v(-event.value * 5)


class StateD(BaseState):

    def __init__(self, context):
        super().__init__(context)
        self.c = context
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.c.key_leftctrl.press()
            self.c.key_leftshift.press()
            self.c.key_t.press()
        
        else:
            self.c.key_t.release()
            self.c.key_leftshift.release()
            self.c.key_leftctrl.release()

    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 1:
            self.c.key_leftctrl.press()
            self.c.key_w.press()

        else:
            self.c.key_w.release()
            self.c.key_leftctrl.release()
    
    def on_up_click(self, event): # C
        self.clean = False

        if event.value == 1:
            self.c.key_leftalt.press()
            self.c.key_f4.press()

        else:
            self.c.key_f4.release()
            self.c.key_leftalt.release()

    def on_right_click(self, event): # D
        if event.value == 0:

            if self.clean:
                self.c.bt_middle.press()
                self.c.bt_middle.release()
            
            self.c.lockable1.unlock()

            self.c.set_state(self.c.state_N)
    
    def on_move_rel_x(self, event):
        self.clean = False
        self.c.lockable1.update_h(event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        self.c.lockable1.update_v(-event.value * 5)
