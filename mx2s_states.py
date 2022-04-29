from utils import BaseState


class StateN(BaseState): # Normal

    def __init__(self, context):
        super().__init__(context)
    
    def on_left_click(self, event):
        self.c.bt_left.update(event.value)

    def on_middle_click(self, event):
        self.c.bt_middle.update(event.value)
        
    def on_right_click(self, event):
        # Right
        self.c.bt_right.update(event.value)

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            self.c.set_state(self.c.state_H)
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            self.c.set_state(self.c.state_G)
    
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


class StateG(BaseState): # Navigator

    def __init__(self, context):
        super().__init__(context)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.c.key_leftctrl.press()
            self.c.bt_left.press()

        else:
            self.c.bt_left.release()
            self.c.key_leftctrl.release()

    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 0:
            self.c.key_leftctrl.press()
            self.c.key_w.press()
            self.c.key_w.release()
            self.c.key_leftctrl.release()
        
    def on_right_click(self, event): # C
        self.clean = False

        if event.value == 0:
            self.c.key_leftctrl.press()
            self.c.key_leftshift.press()
            self.c.key_t.press()
            self.c.key_t.release()
            self.c.key_leftshift.release()
            self.c.key_leftctrl.release()

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            self.c.set_state(self.c.state_HG)
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G

            if self.clean:
                self.c.key_back.press()
                self.c.key_back.release()

            self.c.set_state(self.c.state_N)
    
    def on_scroll(self, event): # E
        self.clean = False
        self.c.key_tabs.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False

        if event.value != 0:
            self.c.key_leftctrl.press()
            self.c.key_equal.press()

        else:
            self.c.key_equal.release()
            self.c.key_leftctrl.release()
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        
        if event.value != 0:
            self.c.key_leftctrl.press()
            self.c.key_minus.press()
        
        else:
            self.c.key_minus.release()
            self.c.key_leftctrl.release()
    
    def on_move_rel_x(self, event):
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.c.bt_rel_y.update(event.value)


class StateH(BaseState): # Multimedia

    def __init__(self, context):
        super().__init__(context)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        self.c.key_play_pause.update(event.value)

    def on_middle_click(self, event): # B
        self.clean = False
        self.c.key_stop.update(event.value)
        
    def on_right_click(self, event): # C
        self.clean = False
        self.c.key_mute_unmute.update(event.value)

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H

            if self.clean:
                self.c.key_forward.press()
                self.c.key_forward.release()
            
            self.c.set_state(self.c.state_N)
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            self.c.set_state(self.c.state_HG)
    
    def on_scroll(self, event): # E
        self.clean = False
        self.c.key_volume.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        self.clean = False
        self.c.key_next_song.update(event.value)
    
    def on_scroll_right_click(self, event): # F
        self.clean = False
        self.c.key_previous_song.update(event.value)
    
    def on_move_rel_x(self, event):
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        self.c.bt_rel_y.update(event.value)


class StateHG(BaseState): # System

    def __init__(self, context):
        super().__init__(context)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value != 0:
            self.c.key_leftctrl.press()
            self.c.key_z.press()
        else:
            self.c.key_z.release()
            self.c.key_leftctrl.release()


    def on_middle_click(self, event): # B
        self.clean = False

        if event.value == 1:
            self.c.key_leftalt.press()
            self.c.key_f4.press()
        elif event.value == 0:
            self.c.key_f4.release()
            self.c.key_leftalt.release()
        
    def on_right_click(self, event): # C
        self.clean = False
        
        if event.value != 0:
            self.c.key_leftctrl.press()
            self.c.key_leftshift.press()
            self.c.key_z.press()
        else:
            self.c.key_z.release()
            self.c.key_leftshift.release()
            self.c.key_leftctrl.release()

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            self.c.set_state(self.c.state_G)
            self.c.state_G.clean = False

            if self.clean:
                self.c.key_leftmeta.press()
                self.c.key_leftmeta.release()
            
            if self.c.alt_mode:
                self.c.alt_mode = False
                self.c.key_leftalt.release()
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            self.c.set_state(self.c.state_H)
            self.c.state_H.clean = False

            if self.clean:
                self.c.key_leftmeta.press()
                self.c.key_leftmeta.release()
            
            if self.c.alt_mode:
                self.c.alt_mode = False
                self.c.key_leftalt.release()
    
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
