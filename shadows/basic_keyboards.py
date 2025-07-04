from shadows.virtual_keyboard import VirtualKeyboardEvent

from evdev import ecodes as e
from reflex import Reflex

import log


# If you want to intercept more keybords, add them here
# Get their names using "sudo lsusb" ou "sudo evtest"
# TODO: Find a way to automatically do this

TARGET_DEVICES = [
    "CORSAIR CORSAIR K63 Wireless Mechanical Gaming Keyboard", 
    "CORSAIR CORSAIR K63 Wireless USB Receiver Keyboard", 
    "CORSAIR CORSAIR K63 Wireless USB Receiver", 
    "HyperX HyperX Mars Gaming KeyBoard", 
    "MSI  FORGE GK310 ", 
    "LITE-ON Technology USB NetVista Full Width Keyboard.",
]

SOURCE_BASIC_KEYBOARD = "Basic Keyboard"


class BasicKeyboards(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)

        for device in TARGET_DEVICES:
            self.add_listener("DeviceReader:" + device, self.on_event)

    def on_event(self, topic_name, event):
        with VirtualKeyboardEvent(self.mind, SOURCE_BASIC_KEYBOARD) as eb:
            eb.forward(event.type, event.code, event.value)


def on_load(shadow):
    BasicKeyboards(shadow)
    shadow.mind.require_device(TARGET_DEVICES)
