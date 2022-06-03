from deploys.device_writer import OutputEvent
from evdev import ecodes as e
from node import Node

import log


# If you want to intercept more keybords, add them here
# Get their names using "sudo lsusb" ou "sudo evtest"
# TODO?: Find a way to automatically do this
TARGET_DEVICES = [
    "CORSAIR CORSAIR K63 Wireless Mechanical Gaming Keyboard", 
    "CORSAIR CORSAIR K63 Wireless USB Receiver Keyboard", 
    "CORSAIR CORSAIR K63 Wireless USB Receiver", 
]


class BasicKeyboards(Node):

    def __init__(self, deploy):
        super().__init__(deploy)

        for device in TARGET_DEVICES:
            self.add_listener("DeviceReader:" + device, self.on_event)

    def on_event(self, topic_name, event):
        with OutputEvent(self.core) as eb:
            eb.forward(event.type, event.code, event.value)


def on_load(deploy):
    BasicKeyboards(deploy)
    deploy.core.require_device(TARGET_DEVICES)
