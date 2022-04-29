#!/usr/bin/env python3

from marble_states import StateN, StateB, StateC, StateD
from utils import run_main_loop, Context
from evdev import ecodes as e
import os

os.nice(-20)

c = Context("virtual_marble")
c.state_N  = StateN(c)
c.state_B  = StateB(c)
c.state_C  = StateC(c)
c.state_D  = StateD(c)
c.state    = c.state_N

def event_processor(event):

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

run_main_loop("Logitech USB Trackball", event_processor, c)
