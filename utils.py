# from this import d
from evdev import list_devices, InputDevice, AbsInfo, UInput, ecodes as e
from keys import Key, WheelKey, DirectKey, DelayedKey, LockableDelayedKey

import traceback
import time
import sys


def grab_device(name):
    devices = [InputDevice(path) for path in list_devices()]
    for d in devices:
        if d.name == name:
            d.grab()
            return d
    return None


def smooth(v):
    return int(v * 1.5)


def run_main_loop(device_name, event_processor, context):

    while True:
        try:
            dev = grab_device(device_name)

            if dev is None:
                print(device_name + " not found, retrying in 3s")
                time.sleep(3)
            
            else:
                print("Connected to " + device_name)

                for event in dev.read_loop():
                    event_processor(event)
            
        except OSError:
            print("OSError, resuming in 3s")
            traceback.print_exc(file=sys.stdout)
            time.sleep(3)
        
        except KeyboardInterrupt:
            break

    if dev is not None:
        dev.close()

    if context is not None:
        context.close()
    
    print("Bye")


class BaseState:

    def __init__(self, context):
        self.c = context

    def on_deactivate(self):
        if self.c.alt_mode:
            self.c.alt_mode = False
            self.c.key_leftalt.release()

    def on_activate(self):
        pass


class Context:

    def __init__(self, vdev_name):

        cap = {
            e.EV_KEY : [
                e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, 
                e.KEY_TAB, e.KEY_LEFTALT, e.KEY_LEFTCTRL, e.KEY_LEFTSHIFT, e.KEY_LEFTMETA, 
                e.KEY_C, e.KEY_D, e.KEY_X, e.KEY_V, e.KEY_S, e.KEY_T, e.KEY_W, e.KEY_Y, e.KEY_Z, 
                e.KEY_PLAYPAUSE, e.KEY_NEXTSONG, e.KEY_PREVIOUSSONG, e.KEY_STOPCD, 
                e.KEY_MUTE, e.KEY_VOLUMEUP, e.KEY_VOLUMEDOWN, e.KEY_PRESENTATION, 
                e.KEY_MINUS, e.KEY_EQUAL, e.KEY_F4, e.KEY_ESC,
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

        self.vdev     = UInput(cap, name=vdev_name, version=0x3)
        self.alt_mode = False

        self.bt_right  = Key("right",  self.vdev, e.EV_KEY, e.BTN_RIGHT,  90001)
        self.bt_left   = Key("left",   self.vdev, e.EV_KEY, e.BTN_LEFT,   90004)
        self.bt_middle = Key("middle", self.vdev, e.EV_KEY, e.BTN_MIDDLE, 90005)

        self.bt_rel_x   = DirectKey("rel_x",  self.vdev, e.EV_REL, e.REL_X)
        self.bt_rel_y   = DirectKey("rel_y",  self.vdev, e.EV_REL, e.REL_Y)
        self.bt_wheel_h = WheelKey("wheel_h", self.vdev, e.EV_REL, e.REL_HWHEEL, e.REL_HWHEEL_HI_RES, 120)
        self.bt_wheel_v = WheelKey("wheel_v", self.vdev, e.EV_REL, e.REL_WHEEL,  e.REL_WHEEL_HI_RES,  120)

        self.key_play_pause    = Key("KEY_PLAYPAUSE",          self.vdev, e.EV_KEY, e.KEY_PLAYPAUSE)
        self.key_next_song     = Key("KEY_NEXT",               self.vdev, e.EV_KEY, e.KEY_NEXTSONG)
        self.key_previous_song = Key("KEY_PREVIOUSSONG",       self.vdev, e.EV_KEY, e.KEY_PREVIOUSSONG)
        self.key_stop          = Key("KEY_STOP_CD",            self.vdev, e.EV_KEY, e.KEY_STOPCD)
        self.key_mute_unmute   = Key("KEY_MUTE",               self.vdev, e.EV_KEY, e.KEY_MUTE)
        self.key_volume_up     = Key("KEY_VOLUME_UP",          self.vdev, e.EV_KEY, e.KEY_VOLUMEUP)
        self.key_volume_down   = Key("KEY_VOLUME_DOWN",        self.vdev, e.EV_KEY, e.KEY_VOLUMEDOWN)
        self.key_equal         = Key("KEY_EQUAL",              self.vdev, e.EV_KEY, e.KEY_EQUAL)
        self.key_minus         = Key("KEY_MINUS",              self.vdev, e.EV_KEY, e.KEY_MINUS)
        self.key_escape        = Key("KEY_ESCAPE",             self.vdev, e.EV_KEY, e.KEY_ESC)

        self.key_volume   = DelayedKey("DELAYED_VOLUME",   self.on_update_volume,  200)
        self.key_tabs     = DelayedKey("DELAYED_CTRLTAB",  self.on_switch_tabs,    500)
        self.key_windows  = DelayedKey("DELAYED_ALTTAB",   self.on_switch_windows, 500)
        self.key_zoom     = DelayedKey("DELAYED_ZOOM",     self.on_switch_zoom,    200)
        self.key_undoredo = DelayedKey("DELAYED_UNDOREDO", self.on_undo_redo,      200)

        self.key_leftmeta  = Key("leftmeta",  self.vdev, e.EV_KEY, e.KEY_LEFTMETA)
        self.key_leftalt   = Key("leftalt",   self.vdev, e.EV_KEY, e.KEY_LEFTALT)
        self.key_leftctrl  = Key("leftctrl",  self.vdev, e.EV_KEY, e.KEY_LEFTCTRL)
        self.key_leftshift = Key("leftshift", self.vdev, e.EV_KEY, e.KEY_LEFTSHIFT)
        self.key_tab       = Key("tab",       self.vdev, e.EV_KEY, e.KEY_TAB)
        self.key_back      = Key("back",      self.vdev, e.EV_KEY, e.BTN_SIDE,  90004)
        self.key_forward   = Key("forward",   self.vdev, e.EV_KEY, e.BTN_EXTRA, 90005)
        self.key_c         = Key("key_c",     self.vdev, e.EV_KEY, e.KEY_C)
        self.key_d         = Key("key_d",     self.vdev, e.EV_KEY, e.KEY_D)
        self.key_s         = Key("key_s",     self.vdev, e.EV_KEY, e.KEY_S)
        self.key_t         = Key("key_t",     self.vdev, e.EV_KEY, e.KEY_T)
        self.key_v         = Key("key_v",     self.vdev, e.EV_KEY, e.KEY_V)
        self.key_w         = Key("key_w",     self.vdev, e.EV_KEY, e.KEY_W)
        self.key_x         = Key("key_x",     self.vdev, e.EV_KEY, e.KEY_X)
        self.key_y         = Key("key_y",     self.vdev, e.EV_KEY, e.KEY_Y)
        self.key_z         = Key("key_z",     self.vdev, e.EV_KEY, e.KEY_Z)
        self.key_f4        = Key("key_f4",    self.vdev, e.EV_KEY, e.KEY_F4)

        self.lockable1     = LockableDelayedKey("lockable1", self.on_switch_windows, self.on_switch_tabs, 400)
        self.lockable2     = LockableDelayedKey("lockable2", self.on_undo_redo, self.on_update_volume, 300)
    
    def on_undo_redo(self, value):
        if value:
            self.key_leftctrl.press()
            self.key_y.press()
            self.key_y.release()
            self.key_leftctrl.release()

        else:
            self.key_leftctrl.press()
            self.key_z.press()
            self.key_z.release()
            self.key_leftctrl.release()
    
    def on_switch_zoom(self, value):
        if value:
            self.key_leftctrl.press()
            self.key_equal.press()
            self.key_equal.release()
            self.key_leftctrl.release()

        else:
            self.key_leftctrl.press()
            self.key_minus.press()
            self.key_minus.release()
            self.key_leftctrl.release()
    
    def on_switch_tabs(self, value):
        if value:
            self.key_leftctrl.press()
            self.key_leftshift.press()
            self.key_tab.press()
            self.key_tab.release()
            self.key_leftshift.release()
            self.key_leftctrl.release()

        else:
            self.key_leftctrl.press()
            self.key_tab.press()
            self.key_tab.release()
            self.key_leftctrl.release()
    
    def on_switch_windows(self, value):
        if not self.alt_mode:
            self.alt_mode = True
            self.key_leftalt.press()
        
        if value:
            self.key_tab.press()
            self.key_tab.release()

        else:
            self.key_leftshift.press()
            self.key_tab.press()
            self.key_tab.release()
            self.key_leftshift.release()
    
    def on_update_volume(self, value):
        if value:
            self.key_volume_up.press()
            self.key_volume_up.release()

        else:
            self.key_volume_down.press()
            self.key_volume_down.release()
    
    def set_state(self, state):
        self.state.on_deactivate()
        self.state = state
        self.state.on_activate()

    def close(self):
        if self.vdev is not None:
            self.vdev.close()
