
from utils import warn, error, info, debug, BaseNode
from subprocess import Popen, PIPE

import shlex
import time

TOPIC_LOGIN_CHANGED = "LoginChanged"


class WatchLogin(BaseNode):

    def __init__(self, core):
        super().__init__(core)
        self.start()

    def run(self):
        self.done = False

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
                        error("returncode:", str(proc.returncode), "error_msg:", error_msg)
                        break

                    if "CLOSE_WRITE" in line:
                        logins = self.get_logins()
                        self.core.emit(TOPIC_LOGIN_CHANGED, logins)

                        # for login in logins:
                        #     info("Login entry:", login)

                    # if "WM_CLASS(STRING)" in props:
                    #     info("Changed to window:", props["WM_CLASS(STRING)"])
                    #     wm_class = props["WM_CLASS(STRING)"].replace("\"", "").split(", ")
                    #     self.core.emit(TOPIC_WINDOW_CHANGED, wm_class)
            except Exception as e:
                error("Fail during login monitoring, retrying in 3s...", e)
            
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
                username = line[:line.index(" ")]
                logins.append(username)
        
        return logins


def on_load(core):
    core.add_node(WatchLogin(core))

