from evdev import AbsInfo, UInput, ecodes as e
from keys import Key, WheelKey, DirectKey, DelayedKey

class Context:

    def __init__(self):

        cap = {
            e.EV_KEY : [
                e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, 
                e.KEY_TAB, e.KEY_LEFTALT, e.KEY_LEFTCTRL, e.KEY_LEFTSHIFT, 
                e.KEY_C, e.KEY_X, e.KEY_V, e.KEY_T, e.KEY_W, e.KEY_Y, e.KEY_Z,
                e.KEY_PLAYPAUSE, e.KEY_NEXTSONG, e.KEY_PREVIOUSSONG, e.KEY_STOPCD, 
                e.KEY_MUTE, e.KEY_VOLUMEUP, e.KEY_VOLUMEDOWN,
                e.KEY_MINUS, e.KEY_EQUAL, e.KEY_F4,
            ],
            e.EV_REL : [
                (e.REL_X, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_Y, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)),
                (e.REL_WHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_HWHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_WHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_HWHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)),
            ]
        }

        self.vdev     = UInput(cap, name="virtualMX2S", version=0x3)
        self.alt_mode = False

        self.bt_right  = Key("right",  self.vdev, e.EV_KEY, e.BTN_RIGHT,  90001)
        self.bt_left   = Key("left",   self.vdev, e.EV_KEY, e.BTN_LEFT,   90004)
        self.bt_middle = Key("middle", self.vdev, e.EV_KEY, e.BTN_MIDDLE, 90005)

        self.bt_rel_x   = DirectKey("rel_x",  self.vdev, e.EV_REL, e.REL_X)
        self.bt_rel_y   = DirectKey("rel_y",  self.vdev, e.EV_REL, e.REL_Y)
        self.bt_wheel_h = WheelKey("wheel_h", self.vdev, e.EV_REL, e.REL_HWHEEL, e.REL_HWHEEL_HI_RES, 120, 1)
        self.bt_wheel_v = WheelKey("wheel_v", self.vdev, e.EV_REL, e.REL_WHEEL,  e.REL_WHEEL_HI_RES,  120, 1)

        self.key_play_pause    = Key("KEY_PLAYPAUSE",          self.vdev, e.EV_KEY, e.KEY_PLAYPAUSE)
        self.key_next_song     = Key("KEY_NEXT",               self.vdev, e.EV_KEY, e.KEY_NEXTSONG)
        self.key_previous_song = Key("KEY_PREVIOUSSONG",       self.vdev, e.EV_KEY, e.KEY_PREVIOUSSONG)
        self.key_stop          = Key("KEY_STOP_CD",            self.vdev, e.EV_KEY, e.KEY_STOPCD)
        self.key_mute_unmute   = Key("KEY_MUTE",               self.vdev, e.EV_KEY, e.KEY_MUTE)
        self.key_volume_up     = Key("KEY_VOLUME_UP",          self.vdev, e.EV_KEY, e.KEY_VOLUMEUP)
        self.key_volume_down   = Key("KEY_VOLUME_DOWN",        self.vdev, e.EV_KEY, e.KEY_VOLUMEDOWN)
        self.key_equal         = Key("KEY_EQUAL",              self.vdev, e.EV_KEY, e.KEY_EQUAL)
        self.key_minus         = Key("KEY_MINUS",              self.vdev, e.EV_KEY, e.KEY_MINUS)

        self.key_volume   = DelayedKey("DELAYED_VOLUME",   self.vdev, self.on_update_volume,  200)
        self.key_tabs     = DelayedKey("DELAYED_CTRLTAB",  self.vdev, self.on_switch_tabs,    200)
        self.key_windows  = DelayedKey("DELAYED_ALTTAB",   self.vdev, self.on_switch_windows, 200)
        self.key_zoom     = DelayedKey("DELAYED_ZOOM",     self.vdev, self.on_switch_zoom,    200)
        self.key_undoredo = DelayedKey("DELAYED_UNDOREDO", self.vdev, self.on_undo_redo,      400)

        self.key_leftalt   = Key("leftalt",   self.vdev, e.EV_KEY, e.KEY_LEFTALT)
        self.key_leftctrl  = Key("leftctrl",  self.vdev, e.EV_KEY, e.KEY_LEFTCTRL)
        self.key_leftshift = Key("leftshift", self.vdev, e.EV_KEY, e.KEY_LEFTSHIFT)
        self.key_tab       = Key("tab",       self.vdev, e.EV_KEY, e.KEY_TAB)
        self.key_back      = Key("back",      self.vdev, e.EV_KEY, e.BTN_SIDE,  90004)
        self.key_forward   = Key("forward",   self.vdev, e.EV_KEY, e.BTN_EXTRA, 90005)
        self.key_c         = Key("key_c",     self.vdev, e.EV_KEY, e.KEY_C)
        self.key_t         = Key("key_t",     self.vdev, e.EV_KEY, e.KEY_T)
        self.key_v         = Key("key_v",     self.vdev, e.EV_KEY, e.KEY_V)
        self.key_w         = Key("key_w",     self.vdev, e.EV_KEY, e.KEY_W)
        self.key_x         = Key("key_x",     self.vdev, e.EV_KEY, e.KEY_X)
        self.key_y         = Key("key_y",     self.vdev, e.EV_KEY, e.KEY_Y)
        self.key_z         = Key("key_z",     self.vdev, e.EV_KEY, e.KEY_Z)
        self.key_f4        = Key("key_f4",    self.vdev, e.EV_KEY, e.KEY_F4)
    
    def on_undo_redo(self, value):
        if value:
            self.key_leftctrl.update(1)
            self.key_y.update(1)
            self.key_y.update(0)
            self.key_leftctrl.update(0)

        else:
            self.key_leftctrl.update(1)
            self.key_z.update(1)
            self.key_z.update(0)
            self.key_leftctrl.update(0)
    
    def on_switch_zoom(self, value):
        if value:
            self.key_leftctrl.update(1)
            self.key_equal.update(1)
            self.key_equal.update(0)
            self.key_leftctrl.update(0)

        else:
            self.key_leftctrl.update(1)
            self.key_minus.update(1)
            self.key_minus.update(0)
            self.key_leftctrl.update(0)
    
    def on_switch_tabs(self, value):
        if value:
            self.key_leftctrl.update(1)
            self.key_leftshift.update(1)
            self.key_tab.update(1)
            self.key_tab.update(0)
            self.key_leftshift.update(0)
            self.key_leftctrl.update(0)

        else:
            self.key_leftctrl.update(1)
            self.key_tab.update(1)
            self.key_tab.update(0)
            self.key_leftctrl.update(0)
    
    def on_switch_windows(self, value):
        if not self.alt_mode:
            self.alt_mode = True
            self.key_leftalt.update(1)
        
        if value:
            self.key_tab.update(1)
            self.key_tab.update(0)

        else:
            self.key_leftshift.update(1)
            self.key_tab.update(1)
            self.key_tab.update(0)
            self.key_leftshift.update(0)
    
    def on_update_volume(self, value):
        if value:
            self.key_volume_up.update(1)
            self.key_volume_up.update(0)

        else:
            self.key_volume_down.update(1)
            self.key_volume_down.update(0)
    
    def close(self):
        if self.vdev is not None:
            self.vdev.close()


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
            self.c.key_leftctrl.update(1)
            self.c.bt_left.update(1)

        else:
            self.c.bt_left.update(0)
            self.c.key_leftctrl.update(0)


    def on_middle_click(self, event): # B
        if event.value == 0:
            self.c.key_leftctrl.update(1)
            self.c.key_w.update(1)
            self.c.key_w.update(0)
            self.c.key_leftctrl.update(0)
        
    def on_right_click(self, event): # C
        if event.value == 0:
            self.c.key_leftctrl.update(1)
            self.c.key_leftshift.update(1)
            self.c.key_t.update(1)
            self.c.key_t.update(0)
            self.c.key_leftshift.update(0)
            self.c.key_leftctrl.update(0)

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
            self.c.key_leftctrl.update(1)
            self.c.key_equal.update(1)
        else:
            self.c.key_equal.update(0)
            self.c.key_leftctrl.update(0)
    
    def on_scroll_right_click(self, event): # F
        
        if event.value == 1:
            self.c.key_leftctrl.update(1)
            self.c.key_minus.update(1)
        else:
            self.c.key_minus.update(0)
            self.c.key_leftctrl.update(0)
    
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


# class StateEdit: # GH

#     def __init__(self, context):
#         self.c = context
    
#     def on_left_click(self, event): # A
#         if event.value == 1:
#             self.c.key_leftctrl.update(1)
#             self.c.key_c.update(1)
#         else:
#             self.c.key_c.update(0)
#             self.c.key_leftctrl.update(0)

#     def on_middle_click(self, event): # B
#         if event.value == 1:
#             self.c.key_leftctrl.update(1)
#             self.c.key_x.update(1)
#         else:
#             self.c.key_x.update(0)
#             self.c.key_leftctrl.update(0)
        
#     def on_right_click(self, event): # C
#         if event.value == 1:
#             self.c.key_leftctrl.update(1)
#             self.c.key_v.update(1)
#         else:
#             self.c.key_v.update(0)
#             self.c.key_leftctrl.update(0)

#     def on_side_up_click(self, event): # H
#         if event.value == 0: # -H
#             # Move to browser state 
#             self.c.state = self.c.state_G
    
#     def on_side_down_click(self, event): # G
#         if event.value == 0: # -G
#             # Move to multimedia state
#             self.c.state = self.c.state_H
    
#     def on_scroll(self, event): # E
#         pass
#         # self.c.key_undoredo.update(event.value)
    
#     def on_scroll_left_click(self, event): # D
#         # pass
#         if event.value == 1:
#             self.c.key_leftctrl.update(1)
#             self.c.key_y.update(1)
#         else:
#             self.c.key_y.update(0)
#             self.c.key_leftctrl.update(0)

#     def on_scroll_right_click(self, event): # F
#         # pass
#         if event.value == 1:
#             self.c.key_leftctrl.update(1)
#             self.c.key_z.update(1)
#         else:
#             self.c.key_z.update(0)
#             self.c.key_leftctrl.update(0)

    
#     def on_move_rel_x(self, event):
#         # Horizontal movement
#         self.c.bt_rel_x.update(event.value)

#     def on_move_rel_y(self, event):
#         # Vertical movement
#         self.c.bt_rel_y.update(event.value)


class StateSystem: # HG

    def __init__(self, context):
        self.c = context
    
    def on_left_click(self, event): # A
        if event.value == 1:
            self.c.key_leftctrl.update(1)
            self.c.key_z.update(1)
        else:
            self.c.key_z.update(0)
            self.c.key_leftctrl.update(0)

    def on_middle_click(self, event): # B
        if event.value == 1:
            self.c.key_leftalt.update(1)
            self.c.key_f4.update(1)
        else:
            self.c.key_f4.update(0)
            self.c.key_leftalt.update(0)
        
    def on_right_click(self, event): # C
        if event.value == 1:
            self.c.key_leftctrl.update(1)
            self.c.key_y.update(1)
        else:
            self.c.key_y.update(0)
            self.c.key_leftctrl.update(0)

    def on_side_up_click(self, event): # H
        if event.value == 0: # -H
            # Move to browser state 
            self.c.state = self.c.state_G

            if self.c.alt_mode:
                self.c.alt_mode = False
                self.c.key_leftalt.update(0)
    
    def on_side_down_click(self, event): # G
        if event.value == 0: # -G
            # Move to multimedia state
            self.c.state = self.c.state_H

            if self.c.alt_mode:
                self.c.alt_mode = False
                self.c.key_leftalt.update(0)
    
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
