from utils import BaseNode, debug, info, warn, error
from nodes.watch_login import TOPIC_LOGIN_CHANGED


class Dispatcher(BaseNode):

    def __init__(self, core):
        super().__init__(core)
        self.current_user = None
        core.register_listener(self, TOPIC_LOGIN_CHANGED, self.on_login_changed)

    def on_login_changed(self, topic_name, event):
        if self.current_user is None:
            if len(event) != 0:
                self.current_user = event[0]
                info("User is active, name is ", self.current_user)
                self.core.load_package("watch_windows", self.current_user)

        else:
            if len(event) == 0:
                info("User is inactive")
                self.core.unload_package("watch_windows", self.current_user)
                self.current_user = None



def on_load(core):
    core.add_node(Dispatcher(core))

# def on_unload(core):
#     core.remove_node("Dispatcher")

