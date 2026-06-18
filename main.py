#!/usr/bin/env python3

import sys
import log
import os

import shadows
from mind import Mind
# from shadows import VirtualMouse, VirtualKeyboard, LogitechMXMaster3S, WatchDevices, Dispatcher, BasicKeyboards, WatchLogin, SmartOutput, MacroKeyboard


os.nice(-20)
log.init_logger("DEBUG" if len(sys.argv) == 1 else sys.argv[1])


mind = Mind()

# Output shadows

mind.add_shadow(shadows.VirtualKeyboard())
mind.add_shadow(shadows.VirtualMouse())
# mind.add_shadow("virtual_pen")

# Input shadows

# mind.add_shadow("logitech_marble")
# mind.add_shadow("vostro_keyboard")
mind.add_shadow(shadows.BasicKeyboards())
mind.add_shadow(shadows.MacroKeyboard())
mind.add_shadow(shadows.LogitechMX2S())
mind.add_shadow(shadows.LogitechMXMaster3S())
mind.add_shadow(shadows.NuleaM512())
#mind.add_shadow("xppen_deco_pro")

# System shadows

mind.add_shadow(shadows.Dispatcher())
mind.add_shadow(shadows.WatchLogin())
mind.add_shadow(shadows.WatchDevices())

# Intelligence shadows

mind.add_shadow(shadows.SmartOutput())

# Main loop

mind.run()
