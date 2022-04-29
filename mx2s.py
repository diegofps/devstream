#!/usr/bin/env python3

from mx2s_states import StateN, StateG, StateH, StateHG
from utils import run_main_loop, Context
from evdev import ecodes as e
import os

os.nice(-20)

c = Context("virtual_mx2s")
c.state_N  = StateN(c)
c.state_G  = StateG(c)
c.state_H  = StateH(c)
c.state_HG = StateHG(c)
c.state    = c.state_N


def event_processor(event):

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

run_main_loop("Logitech MX Anywhere 2S", event_processor, c)

print("Bye")
