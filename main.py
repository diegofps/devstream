#!/usr/bin/env python3

from utils import Core, init_logger
import sys
import os

os.nice(-20)

if len(sys.argv) == 1:
    init_logger("DEBUG")
else:
    init_logger(sys.argv[1])

core = Core()
core.start()

