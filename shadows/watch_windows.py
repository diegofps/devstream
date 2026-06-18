
from subprocess import Popen, PIPE
from reflex import Reflex
from shadow import Shadow

import shlex
import time
import log


TOPIC_WINDOW_CHANGED = "WindowChanged"


class WatchWindowsReflex(Reflex):

    def __init__(self, username, display, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.display = display

        log.info(f"Creating {self.name}: username={username}, display={display}")
    
    def on_configure(self):
        self.require_daemon()

    def run(self, daemon):

        while not daemon.done:
            try:
                cmd  = shlex.split("su %s -c 'xprop -spy -root _NET_ACTIVE_WINDOW -display %s'" % (self.username, self.display))
                proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
                
                while True:
                    line = proc.stdout.readline().decode("utf-8")

                    if daemon.done:
                        break

                    if line is None or line == "":
                        error_msg = proc.stderr.readlines()
                        log.error("returncode:", str(proc.returncode), "error_mmsg:", error_msg)
                        proc.kill()
                        break

                    idd = line[40:-1]
                    props = self.get_window_props(idd)

                    if not props:
                        proc.kill()
                        log.warn("WatchWindow was unable to detect the current window, restarting the monitor in 2s.")
                        time.sleep(2)
                        break

                    window_class = ""
                    app_name = ""
                    window_name = ""

                    if "WM_CLASS(STRING)" in props:
                        window_class, app_name = props["WM_CLASS(STRING)"].replace("\"", "").split(", ")
                    
                    if "WM_NAME(STRING)" in props:
                        window_name = props["WM_NAME(STRING)"]
                    
                    log.info(f"Window focused: window_class='{window_class}', app_name='{app_name}', window_name='{window_name}'")
                    self.mind.emit(TOPIC_WINDOW_CHANGED, (window_class, app_name, window_name))
            except Exception as e:
                log.error("Fail during window monitoring, retrying in 3s...", e)
                time.sleep(3)
    
        log.info("WatchWindows is terminating gracefully")

    def get_window_props(self, idd):
        if idd is None or idd == "" or idd == "0x0":
            return {}
        
        cmd   = shlex.split("su %s -c 'xprop -display %s -id %s'" % (self.username, self.display, idd))
        props = {}

        with Popen(cmd, stdout=PIPE) as proc:
            lines = proc.stdout.readlines()
        
        for line in lines:
            line  = line.decode("utf-8")
            cells = line.split("=", 1)
        
            if len(cells) != 2:
                cells = line.split(":", 1)
        
            if len(cells) != 2:
                continue
        
            key = cells[0].strip()
            value = cells[1].strip()
            props[key] = value
        
        return props


class WatchWindows(Shadow):

    def __init__(self, username, display, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.display = display
    
    def on_configure(self):
        self.add_reflex(WatchWindowsReflex(self.username, self.display, autostart=True))


# def on_load(shadow, username, display):
#     WatchWindowsReflex(shadow, username, display)

