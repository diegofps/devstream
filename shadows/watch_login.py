from subprocess import Popen, PIPE
from reflex import Reflex

import shlex
import time
import log

TOPIC_LOGIN_CHANGED = "LoginChanged"


class WatchLogin(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.start()

    def run(self):
        self.done = False

        logins = self.get_logins()
        self.mind.emit(TOPIC_LOGIN_CHANGED, logins)

        while not self.done:
            try:
                cmd = shlex.split("inotifywait -m /var/run/utmp")
                # debug("WatchLogin event, cmd:", cmd)
                proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
                
                while True:
                    line = proc.stdout.readline().decode("utf-8")
                    # debug("WatchLogin event, line:", line)

                    if line is None or line == "":
                        error_msg = proc.stderr.readlines()
                        log.error("returncode:", str(proc.returncode), "error_msg:", error_msg)
                        break

                    if "CLOSE_WRITE" in line:
                        logins = self.get_logins()
                        self.mind.emit(TOPIC_LOGIN_CHANGED, logins)

            except Exception as e:
                log.error("Fail during login monitoring, retrying in 3s...", e)
            
            time.sleep(3)

    def get_logins(self):
        cmd = shlex.split("last -f /var/run/utmp")
        proc = Popen(cmd, stdout=PIPE)
        logins = []
        
        for line in proc.stdout.readlines():
            line = line.decode("utf-8")

            if line == "":
                break

            if "still logged in" in line:
                username, display = line.split()[:2]
                
                if ":" in display:
                    logins.append((username, display))
        
        # log.debug(logins)
        return logins


def on_load(shadow):
    WatchLogin(shadow)

