from subprocess import Popen, PIPE
from reflex import Reflex
from shadow import Shadow

import shlex
import time


TOPIC_LOGIN_CHANGED = "LoginChanged"


class WatchLoginReflex(Reflex):

    def on_configure(self):
        self.require_daemon()

    def run(self, daemon):
        logins = self.get_logins()
        self.mind.emit(TOPIC_LOGIN_CHANGED, logins)

        while not daemon.done:
            try:
                cmd = shlex.split("inotifywait -m /var/run/utmp")
                proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
                
                while True:
                    line = proc.stdout.readline().decode("utf-8")
                    # debug("WatchLogin event, line:", line)

                    if daemon.done:
                        break

                    if line is None or line == "":
                        error_msg = proc.stderr.readlines()
                        self.log.error("returncode:", str(proc.returncode), "error_msg:", error_msg)
                        break

                    if "CLOSE_WRITE" in line:
                        logins = self.get_logins()
                        self.mind.emit(TOPIC_LOGIN_CHANGED, logins)

            except Exception as e:
                self.log.error("Fail during login monitoring, retrying in 3s...", e)
            
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
        
        return logins


class WatchLogin(Shadow):
    def on_configure(self):
        super().on_configure()
        self.add_reflex(WatchLoginReflex, autostart=True)

