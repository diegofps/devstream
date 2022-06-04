from shadows.watch_login import TOPIC_LOGIN_CHANGED
from reflex import Reflex

import log


class Dispatcher(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        
        self.username = None
        self.display = None

        self.add_listener(TOPIC_LOGIN_CHANGED, self.on_login_changed)

    def on_login_changed(self, topic_name, event):
        if self.username is None and self.display is None:
            if len(event) != 0:
                self.username, self.display = event[0]
                log.info("User is now active, name =", self.username, "and display =", self.display)
                self.mind.add_shadow("watch_windows", self.username, self.display)

        else:
            if len(event) == 0:
                log.info("User is inactive")
                self.mind.remove_shadow("watch_windows")
                self.username = None
                self.display = None

def on_load(shadow):
    Dispatcher(shadow)
