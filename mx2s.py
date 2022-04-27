#!/usr/bin/env python3

from evdev import ecodes as e
from utils import grab_device, smooth
from mx2s_states import Context, StateNormal, StateBrowser, StateMultimedia, StateSystem

import traceback
import time
import sys
import os

os.nice(-20)

c = Context()
c.state_N  = StateNormal(c)
c.state_G  = StateBrowser(c)
c.state_H  = StateMultimedia(c)
c.state_HG = StateSystem(c)
c.state    = c.state_N

def process_events(dev):

    for event in dev.read_loop():

        if event.type == e.EV_KEY:

            if event.code == e.BTN_LEFT:
                c.state.on_left_click(event)

            elif event.code == e.BTN_MIDDLE:
                c.state.on_middle_click(event)

            elif event.code == e.BTN_RIGHT:
                c.state.on_right_click(event)

            elif event.code == e.BTN_SIDE:
                c.state.on_side_down_click(event)

            elif event.code == e.BTN_EXTRA:
                c.state.on_side_up_click(event)

        elif event.type == e.EV_REL:

            if event.code == e.REL_X:
                c.state.on_move_rel_x(event)

            elif event.code == e.REL_Y:
                c.state.on_move_rel_y(event)

            elif event.code == e.REL_WHEEL_HI_RES:
                c.state.on_scroll(event)

            elif event.code == e.REL_HWHEEL_HI_RES:

                if event.value < 0:
                    event.value = 1
                    c.state.on_scroll_right_click(event)

                    event.value = 0
                    c.state.on_scroll_right_click(event)
                
                else:
                    event.value = 1
                    c.state.on_scroll_left_click(event)

                    event.value = 0
                    c.state.on_scroll_left_click(event)

while True:
    try:
        dev = grab_device("Logitech MX Anywhere 2S")

        if dev is None:
            print("Logitech MX Anywhere 2S not found, resuming in 3s")
            time.sleep(3)
        
        else:
            print("Logitech MX Anywhere 2S connected")
            process_events(dev)
        
    except OSError:
        print("OSError, resuming in 3s")
        traceback.print_exc(file=sys.stdout)
        time.sleep(3)
    
    except KeyboardInterrupt:
        break

if dev is not None:
    dev.close()

if c is not None:
    c.close()

print("Bye")
