class StateNormal: # N

    def __init__(self, context):
        self.c = context
    
    def on_left_click(self, event):
        # Left
        self.c.bt_left.update(event.value)

    def on_middle_click(self, event):
        # Middle
        self.c.bt_middle.update(event.value)
        
    def on_right_click(self, event):
        # Right
        self.c.bt_right.update(event.value)

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            # Move to multimedia state
            self.c.state = self.c.state_H
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            # Move to browser state
            self.c.state = self.c.state_G
    
    def on_scroll(self, event):
        # Vertical scroll
        self.c.bt_wheel_v.update(event.value)
    
    def on_scroll_left_click(self, event):
        # Forward
        self.c.key_forward.update(event.value)
    
    def on_scroll_right_click(self, event):
        # Back
        self.c.key_back.update(event.value)
    
    def on_move_rel_x(self, event):
        # Horizontal movement
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        # Vertical movement
        self.c.bt_rel_y.update(event.value)


class StateBrowser: # G

    def __init__(self, context):
        self.c = context
    
    def on_left_click(self, event): # A
        if event.value == 1:
            self.c.key_leftctrl.press()
            self.c.bt_left.press()

        else:
            self.c.bt_left.release()
            self.c.key_leftctrl.release()


    def on_middle_click(self, event): # B
        if event.value == 0:
            self.c.key_leftctrl.press()
            self.c.key_w.press()
            self.c.key_w.release()
            self.c.key_leftctrl.release()
        
    def on_right_click(self, event): # C
        if event.value == 0:
            self.c.key_leftctrl.press()
            self.c.key_leftshift.press()
            self.c.key_t.press()
            self.c.key_t.release()
            self.c.key_leftshift.release()
            self.c.key_leftctrl.release()

    def on_side_up_click(self, event): # H
        if event.value == 1: # +H
            self.c.state = self.c.state_HG
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            self.c.state = self.c.state_N
    
    def on_scroll(self, event): # E
        self.c.key_tabs.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        if event.value == 1:
            self.c.key_leftctrl.press()
            self.c.key_equal.press()
        else:
            self.c.key_equal.release()
            self.c.key_leftctrl.release()
    
    def on_scroll_right_click(self, event): # F
        
        if event.value == 1:
            self.c.key_leftctrl.press()
            self.c.key_minus.press()
        else:
            self.c.key_minus.release()
            self.c.key_leftctrl.release()
    
    def on_move_rel_x(self, event):
        # Horizontal movement
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        # Vertical movement
        self.c.bt_rel_y.update(event.value)


class StateMultimedia: # H

    def __init__(self, context):
        self.c = context
    
    def on_left_click(self, event): # A
        # Play / pause music
        self.c.key_play_pause.update(event.value)

    def on_middle_click(self, event): # B
        # Stop music
        self.c.key_stop.update(event.value)
        
    def on_right_click(self, event): # C
        # Mute / unmute
        self.c.key_mute_unmute.update(event.value)

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            # Move to normal state 
            self.c.state = self.c.state_N
    
    def on_side_down_click(self, event): # G
        if event.value == 1: # +G
            # Move to system state
            self.c.state = self.c.state_HG
    
    def on_scroll(self, event): # E
        # Change volume
        self.c.key_volume.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        # Next track
        self.c.key_next_song.update(event.value)
    
    def on_scroll_right_click(self, event): # F
        # Previous track
        self.c.key_previous_song.update(event.value)
    
    def on_move_rel_x(self, event):
        # Horizontal movement
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        # Vertical movement
        self.c.bt_rel_y.update(event.value)


class StateSystem: # HG

    def __init__(self, context):
        self.c = context
    
    def on_left_click(self, event): # A
        if event.value == 1:
            self.c.key_leftctrl.press()
            self.c.key_z.press()
        else:
            self.c.key_z.release()
            self.c.key_leftctrl.release()

    def on_middle_click(self, event): # B
        if event.value == 1:
            self.c.key_leftalt.press()
            self.c.key_f4.press()
        else:
            self.c.key_f4.release()
            self.c.key_leftalt.release()
        
    def on_right_click(self, event): # C
        if event.value == 1:
            self.c.key_leftctrl.press()
            self.c.key_y.press()
        else:
            self.c.key_y.release()
            self.c.key_leftctrl.release()

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            # Move to browser state 
            self.c.state = self.c.state_G

            if self.c.alt_mode:
                self.c.alt_mode = False
                self.c.key_leftalt.release()
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            # Move to multimedia state
            self.c.state = self.c.state_H

            if self.c.alt_mode:
                self.c.alt_mode = False
                self.c.key_leftalt.release()
    
    def on_scroll(self, event): # E
        self.c.key_windows.update(event.value)
    
    def on_scroll_left_click(self, event): # D
        pass
    
    def on_scroll_right_click(self, event): # F
        pass
    
    def on_move_rel_x(self, event):
        # Horizontal movement
        self.c.bt_rel_x.update(event.value)

    def on_move_rel_y(self, event):
        # Vertical movement
        self.c.bt_rel_y.update(event.value)
