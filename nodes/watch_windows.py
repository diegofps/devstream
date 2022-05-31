
from utils import warn, error, info, debug, BaseNode
from subprocess import Popen, PIPE
from threading import Thread

import shlex
import time

TOPIC_WINDOW_CHANGED = "WindowChanged"

class WatchWindows(BaseNode):

    def __init__(self, core):
        super().__init__(core, "WatchWindows", None, None)
        self.thread = None
        self.done = False
        self.start()

    def run(self):
        self.done = False

        while not self.done:
            try:
                cmd = shlex.split("xprop -spy -root _NET_ACTIVE_WINDOW")
                proc = Popen(cmd, stdout=PIPE)

                while True:
                    line = proc.stdout.readline()
                    idd = line[40, -1]
                    props = self.get_window_props(idd)

                    if "WM_CLASS(STRING)" in props:
                        info("Changed to window:", props["WM_CLASS(STRING)"])
                        wm_class = props["WM_CLASS(STRING)"]
                        self.core.emit(TOPIC_WINDOW_CHANGED, wm_class)
            except:
                error("Fail during window manager monitoring, retrying in 3s...")
                time.sleep(3)

    def get_window_props(self, idd):
        cmd = shlex.split("xprop -id " + idd.decode("utf-8"))
        proc = Popen(cmd, stdout=PIPE)
        props = {}
        
        for line in proc.stdout.readlines():
            line = line.decode("utf-8")
            cells = line.split("=", 1)
        
            if len(cells) != 2:
                cells = line.split(":", 1)
        
            if len(cells) != 2:
                continue
        
            key = cells[0].strip()
            value = cells[1].strip()
            props[key] = value
        
        return props

