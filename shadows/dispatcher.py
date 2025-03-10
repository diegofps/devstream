from shadows.watch_devices import TOPIC_DEVICE_CONNECTED, TOPIC_DEVICE_DISCONNECTED
from shadows.watch_login import TOPIC_LOGIN_CHANGED
from evdev import InputDevice
from reflex import Reflex

import log


class Dispatcher(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        
        self.username = None
        self.display = None
        self.devices = {}

        self.add_listener(TOPIC_DEVICE_DISCONNECTED, self.on_device_disconnected)
        self.add_listener(TOPIC_DEVICE_CONNECTED, self.on_device_connected)
        self.add_listener(TOPIC_LOGIN_CHANGED, self.on_login_changed)

    def on_device_connected(self, topic_name, event):
        # log.debug("Dispatcher received a device connected event", topic_name, event)
        for device_path in event:
            # log.debug("Checking device at", device_path)
            try:
                # log.info("Device connected:", device_path)
                dev = InputDevice(device_path)

                if dev.name in self.mind.required_devices:
                    # log.debug(f"{dev.name} is a device with interest, starting shadow ...")
                    shadow = self.mind.add_shadow("device_reader", dev)
                    self.devices[device_path] = shadow
                    # log.debug("shadow started!")
                else:
                    log.debug(f"Device is not in required list, skipping: name=\"{dev.name}\", path=\"{dev.path}\"")
            except Exception as e:
                log.warn("Device reading failure:", e)
    
    def on_device_disconnected(self, topic_name, event):
        for device_path in event:
            # log.info("Device disconnected:", device_path)
            # log.debug(",".join(self.devices.keys()))

            if device_path in self.devices:
                shadow = self.devices[device_path]
                self.mind.remove_shadow(shadow.name)
                del self.devices[device_path]

    def on_login_changed(self, topic_name, event):
        log.info("Dispatcher has detected a login change: ", event)

        if self.username is None and self.display is None:
            if len(event) != 0:
                self.username, self.display = event[0]
                log.info(f"User is now identified by name '{self.username}' and display '{self.display}'. Starting WatchWindows.")
                self.mind.add_shadow("watch_windows", self.username, self.display)

        else:
            if len(event) == 0:
                log.info("User is now inactive. Stoping WatchWindows.")
                self.mind.remove_shadow("watch_windows")
                self.username = None
                self.display = None

def on_load(shadow):
    Dispatcher(shadow)
