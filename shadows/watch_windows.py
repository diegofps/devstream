
from subprocess import Popen, PIPE
from reflex import Reflex

import shlex
import time
import log


TOPIC_WINDOW_CHANGED = "WindowChanged"


class WatchWindows(Reflex):

    def __init__(self, shadow, username, display):
        super().__init__(shadow)
        self.username = username
        self.display = display
        self.start()

        # log.debug("Username:", username, "Display:", display)

    def run(self):
        self.done = False

        while not self.done:
            try:
                cmd = shlex.split("su %s -c 'xprop -spy -root _NET_ACTIVE_WINDOW -display %s'" % (self.username, self.display))
                proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
                
                while True:
                    line = proc.stdout.readline().decode("utf-8")

                    if line is None or line == "":
                        error_msg = proc.stderr.readlines()
                        log.error("returncode:", str(proc.returncode), "error_mmsg:", error_msg)
                        break

                    idd = line[40:-1]
                    props = self.get_window_props(idd)

                    name1 = ""
                    name2 = ""
                    name3 = ""

                    if "WM_CLASS(STRING)" in props:
                        name1, name2 = props["WM_CLASS(STRING)"].replace("\"", "").split(", ")
                    
                    if "WM_NAME(STRING)" in props:
                        name3 = props["WM_NAME(STRING)"]
                    
                    log.info("Window changed '%s' '%s' '%s'" % (name1, name2, name3))
                    self.mind.emit(TOPIC_WINDOW_CHANGED, (name1, name2, name3))
            except Exception as e:
                log.error("Fail during window manager monitoring, retrying in 3s...", e)
            
            time.sleep(3)

    def get_window_props(self, idd):
        if idd is None or idd == "" or idd == "0x0":
            return {}
        
        cmd = shlex.split("su %s -c 'xprop -display %s -id %s'" % (self.username, self.display, idd))
        proc = Popen(cmd, stdout=PIPE)
        props = {}
        
        lines = proc.stdout.readlines()

        for line in lines:
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


def on_load(shadow, username, display):
    WatchWindows(shadow, username, display)
