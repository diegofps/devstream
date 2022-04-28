#!/usr/bin/env python3

#import pdb; pdb.set_trace()

from evdev import ecodes as e
from utils import grab_device, Context
from marble_states import StateNormal, StateB, StateD

import traceback
import time
import sys
import os

os.nice(-20)

c = Context("virtual_marble")
c.state_N  = StateNormal(c)
c.state_B  = StateB(c)
c.state_D  = StateD(c)
c.state    = c.state_N

def process_events(dev):

    for event in dev.read_loop():

        if event.type == e.EV_KEY:

            # big_left
            if event.code == e.BTN_LEFT:
                c.state.on_left_click(event)

            # small left
            elif event.code == e.BTN_SIDE:
                c.state.on_down_click(event)                    

            # small right
            elif event.code == e.BTN_EXTRA:
                c.state.on_up_click(event)

            # big right
            elif event.code == e.BTN_RIGHT:
                c.state.on_right_click(event)

        elif event.type == e.EV_REL:

            # Ball rotates horizontally
            if event.code == e.REL_X:
                c.state.on_move_rel_x(event)

            # Ball rotates vertically
            elif event.code == e.REL_Y:
                c.state.on_move_rel_y(event)


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

if c is not None:
    c.close()

print("Bye")
