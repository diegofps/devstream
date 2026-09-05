#!/usr/bin/env python3

import devstreamlog
import sys

devstreamlog.init(folderpath='.', max_backups=5, level="DEBUG" if len(sys.argv) == 1 else sys.argv[1])

from mind import Mind
import shadows
import os

os.nice(-20)

mind = Mind()

# Output shadows

mind.add_shadow(shadows.VirtualKeyboard())
mind.add_shadow(shadows.VirtualMouse())
# mind.add_shadow("virtual_pen")

# Input shadows

# mind.add_shadow("vostro_keyboard")
mind.add_shadow(shadows.BasicKeyboards())
mind.add_shadow(shadows.MacroKeyboard())
mind.add_shadow(shadows.LogitechMarble())
mind.add_shadow(shadows.LogitechMXAnywhere2S())
mind.add_shadow(shadows.LogitechMXMaster3S())
mind.add_shadow(shadows.NuleaM512())
mind.add_shadow(shadows.GulikitKK3Max())
#mind.add_shadow("xppen_deco_pro")

# System shadows

mind.add_shadow(shadows.Dispatcher())
mind.add_shadow(shadows.WatchLogin())
mind.add_shadow(shadows.WatchDevices())

# Intelligence shadows

mind.add_shadow(shadows.SmartOutput())

# Main loop

mind.run()
