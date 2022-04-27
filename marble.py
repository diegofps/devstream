#!/usr/bin/env python3

from evdev import AbsInfo, UInput, ecodes as e
from utils import grab_device, smooth
from keys import Key, DirectKey, WheelKey

import traceback
import time
import sys
import os

os.nice(-20)

cap = {
    e.EV_KEY : [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, e.KEY_TAB, e.KEY_LEFTALT],
    e.EV_REL : [
        (e.REL_X, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
        (e.REL_Y, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)),
        (e.REL_WHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
        (e.REL_HWHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
        (e.REL_WHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
        (e.REL_HWHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0))
    ]
}

vdev = UInput(cap, name="virtualmarble", version=0x3)

def process_events(dev):
    global vdev

    bt_leftalt = Key("leftalt", vdev, e.EV_KEY, e.KEY_LEFTALT)
    bt_tab     = Key("tab",     vdev, e.EV_KEY, e.KEY_TAB)
    bt_right   = Key("right",   vdev, e.EV_KEY, e.BTN_RIGHT, 90001)
    bt_left    = Key("left",    vdev, e.EV_KEY, e.BTN_LEFT, 90004)
    bt_middle  = Key("middle",  vdev, e.EV_KEY, e.BTN_MIDDLE, 90005)
    bt_back    = Key("back",    vdev, e.EV_KEY, e.BTN_SIDE, 90004)
    bt_forward = Key("forward", vdev, e.EV_KEY, e.BTN_EXTRA, 90005)
    bt_rel_x   = DirectKey("rel_x",  vdev, e.EV_REL, e.REL_X)
    bt_rel_y   = DirectKey("rel_y",  vdev, e.EV_REL, e.REL_Y)
    bt_wheel_h = WheelKey("wheel_h", vdev, e.EV_REL, e.REL_HWHEEL, e.REL_HWHEEL_HI_RES, 120, 10)
    bt_wheel_v = WheelKey("wheel_v", vdev, e.EV_REL, e.REL_WHEEL, e.REL_WHEEL_HI_RES, 120, 5)

    state = 0
    tab_mode = 0

    for event in dev.read_loop():

        # Normal mode
        if state == 0:

            if event.type == e.EV_KEY:

                # big_left
                if event.code == e.BTN_LEFT:
                    bt_left.update(event.value)

                # small left
                elif event.code == e.BTN_SIDE:
                    state = event.value

                    # Disable alternate buttons
                    bt_back.update(0)
                    bt_forward.update(0)

                    bt_leftalt.update(0)
                    bt_tab.update(0)
                    tab_mode = 0

                # small right
                elif event.code == e.BTN_EXTRA:
                    bt_right.update(event.value)

                # big right
                elif event.code == e.BTN_RIGHT:
                    bt_middle.update(event.value)

            elif event.type == e.EV_REL:

                # Ball rotates horizontally
                if event.code == e.REL_X:
                    bt_rel_x.update(smooth(event.value))

                # Ball rotates vertically
                elif event.code == e.REL_Y:
                    bt_rel_y.update(smooth(event.value))


        # Alternate mode
        else:
            
            if event.type == e.EV_KEY:

                # big_left
                if event.code == e.BTN_LEFT:
                    # Activate alt mode if not active
                    if tab_mode != 1:
                        tab_mode = 1
                        bt_leftalt.update(1)
                    
                    # Activate/deactivate tab click
                    bt_tab.update(event.value)

                # small left
                elif event.code == e.BTN_SIDE:
                    state = event.value

                    # Disable normal buttons
                    bt_left.update(0)
                    bt_right.update(0)
                    bt_middle.update(0)

                    # Finish Alt+Tab
                    if tab_mode == 1:
                        tab_mode = 0
                        bt_leftalt.update(0)
                
                # small right
                elif event.code == e.BTN_EXTRA:
                    bt_back.update(event.value)

                # big right
                elif event.code == e.BTN_RIGHT:
                    bt_forward.update(event.value)

            elif event.type == e.EV_REL:

                # Ball rotates horizontally
                if event.code == e.REL_X:
                    bt_wheel_h.update(event.value)

                # Ball rotates vertically
                elif event.code == e.REL_Y:
                    bt_wheel_v.update(-event.value)

while True:
    try:
        dev = grab_device("Logitech USB Trackball")

        if dev is None:
            print("Trackball not found, resuming in 3s")
            time.sleep(3)
        
        else:
            print("Trackball connected")
            process_events(dev)
        
    except OSError:
        print("OSError, resuming in 3s")
        traceback.print_exc(file=sys.stdout)
        time.sleep(3)
    
    except KeyboardInterrupt:
        break

if dev is not None:
    dev.close()

if vdev is not None:
    vdev.close()

print("Bye")
