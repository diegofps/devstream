#!/usr/bin/env python3

"""
This is a module docstring
"""

import sys
import os
import log

from mind import Mind


os.nice(-20)


if len(sys.argv) == 1:
    log.init_logger("DEBUG")
else:
    log.init_logger(sys.argv[1])


mind = Mind()
mind.start()
