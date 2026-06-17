from shadows.virtual_keyboard import VirtualKeyboardEvent

# from evdev import ecodes as e
from reflex import Reflex
from shadow import Shadow

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
    "AT Translated Set 2 keyboard", 
]

SOURCE_BASIC_KEYBOARD = "Basic Keyboard"


class BasicKeyboardsReflex(Reflex):
    def on_configure(self):
        for x in TARGET_DEVICES:
            self.add_listener(f"DeviceReader:{x}", self.on_event)

    def on_event(self, topic_name, event):
        # self.debug_event(topic_name, event)
        with VirtualKeyboardEvent(self.mind, SOURCE_BASIC_KEYBOARD) as eb:
            eb.forward(event.type, event.code, event.value)


class BasicKeyboards(Shadow):
    def on_configure(self):
        self.require_device(TARGET_DEVICES)
        self.add_reflex(BasicKeyboardsReflex(autostart=True))
