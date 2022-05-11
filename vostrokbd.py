from utils import BaseConsumer
from evdev import ecodes as e


TARGET_DEVICE = "AT Translated Set 2 keyboard"


class VostroKBD_N(BaseConsumer):

    def __init__(self, core):
        super().__init__(core)

        self.map = {
            e.KEY_F10:e.KEY_PRINT, e.KEY_F11:e.KEY_HOME, e.KEY_F12:e.KEY_END,
            e.KEY_PRINT:e.KEY_F10, e.KEY_HOME:e.KEY_F11, e.KEY_END:e.KEY_F12
        }

    def on_event(self, event):
        if event.type == e.EV_KEY:
            mapping = self.map.get(event.code)
            if mapping is not None:
                event.code = mapping

        self.core.out.forward(event)


def on_init(core):

    core.consumers["VostroKBD_N"] = VostroKBD_N(core)

    core.listeners[TARGET_DEVICE] = core.consumers["VostroKBD_N"]
