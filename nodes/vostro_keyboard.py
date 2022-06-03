from utils import BaseNode, debug, info, warn, error
from nodes.device_writer import OutputEvent
from evdev import ecodes as e


REQUIRED_DEVICES = [
    "AT Translated Set 2 keyboard", 
]


class VostroKeyboard(BaseNode):

    def __init__(self, core):
        super().__init__(core)

        self.vostro_map = {
            e.KEY_F10:e.KEY_PRINT, e.KEY_F11:e.KEY_HOME, e.KEY_F12:e.KEY_END,
            e.KEY_PRINT:e.KEY_F10, e.KEY_HOME:e.KEY_F11, e.KEY_END:e.KEY_F12, 
        }

        for device_name in REQUIRED_DEVICES:
            core.register_listener(self, "DeviceReader:" + device_name, self.on_event)

    def on_event(self, device_name, event):
        if event.type == e.EV_KEY:
            mapping = self.vostro_map.get(event.code)
            if mapping is not None:
                event.code = mapping
        
        with OutputEvent(self.core) as eb:
            eb.forward(event.type, event.code, event.value)


def on_load(core):

    core.add_node(VostroKeyboard(core))
    core.require_device(REQUIRED_DEVICES)
