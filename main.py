#!/usr/bin/env python3

import sys
import log
import os

from mind import Mind
from shadows import VirtualMouse, VirtualKeyboard, LogitechMXMaster3S, WatchDevices, Dispatcher, BasicKeyboards, WatchLogin, SmartOutput, MacroKeyboard


os.nice(-20)
log.init_logger("DEBUG" if len(sys.argv) == 1 else sys.argv[1])


mind = Mind()

# Output shadows

mind.add_shadow(VirtualKeyboard())
mind.add_shadow(VirtualMouse())
# mind.add_shadow("virtual_pen")

# Input shadows

# mind.add_shadow("logitech_marble")
# mind.add_shadow("vostro_keyboard")
mind.add_shadow(BasicKeyboards())
mind.add_shadow(MacroKeyboard()) # mind.add_shadow("macro_keyboard")
# mind.add_shadow("logitech_mx2s")
mind.add_shadow(LogitechMXMaster3S())
# mind.add_shadow("nulea_m512")
#mind.add_shadow("xppen_deco_pro")

# System shadows

mind.add_shadow(Dispatcher())
mind.add_shadow(WatchLogin())
mind.add_shadow(WatchDevices())

# Intelligence shadows

mind.add_shadow(SmartOutput())

# Main loop

mind.run()
