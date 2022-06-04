#!/usr/bin/env python3

from mind import Mind

import log
import sys
import os


os.nice(-20)


if len(sys.argv) == 1:
    log.init_logger("DEBUG")
else:
    log.init_logger(sys.argv[1])


mind = Mind()
mind.start()
