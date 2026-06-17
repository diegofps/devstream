from shadows.watch_devices import TOPIC_DEVICE_CONNECTED, TOPIC_DEVICE_DISCONNECTED
from shadows.watch_login import TOPIC_LOGIN_CHANGED
from shadows.device_reader import DeviceReader
from evdev import InputDevice
from reflex import Reflex
from shadow import Shadow

import log


"""
This class has three responsibilities:
- Monitor newly connected devices and starts the DeviceReader if there is a shadow that has interest on them. (receiving events from WatchDevices)
- Monitor newly removed devices and stop the DeviceReader if it was active. (receiving events from WatchDevices)
- Monitor the user's login state and start / stop the shadow WatchWindows. (receiving events from WatchLogin)
"""
class DispatcherReflex(Reflex):

    def on_configure(self):
        self.username = None
        self.display = None
        self.devices = {}

        self.add_listener(TOPIC_DEVICE_DISCONNECTED, self.on_device_disconnected)
        self.add_listener(TOPIC_DEVICE_CONNECTED, self.on_device_connected)
        self.add_listener(TOPIC_LOGIN_CHANGED, self.on_login_changed)

    def on_device_connected(self, topic_name, event):
        log.debug("Dispatcher received a device connected event", topic_name, event)

        for device_path in event:
            # log.debug("Checking device at", device_path)
            
            try:
                # log.debug("Device connected:", device_path)
                dev = InputDevice(device_path)

                if dev.name in self.mind.required_devices:
                    log.info(f"Device is required, starting DeviceReader for \"{dev.name}\"")
                    shadow = DeviceReader(dev=dev, name=f"DeviceReader:{dev.name}")
                    self.mind.add_shadow(shadow)
                    self.devices[device_path] = (shadow.name, shadow)
                    log.debug(f"DeviceReader shadow started from dispatcher! name={shadow.name}")
                else:
                    log.info(f"Device is not required, skipping \"{dev.name}\", path=\"{dev.path}\"")
            except Exception as e:
                log.warn(f"Device reading failure for {device_path}:", e)
    
    def on_device_disconnected(self, topic_name, event):
        for device_path in event:
            log.info("Device disconnected:", device_path)
            log.debug(",".join(self.devices.keys()))

            if device_path in self.devices:
                shadow_name, _ = self.devices[device_path]
                self.mind.remove_shadow(shadow_name)
                del self.devices[device_path]
                log.debug(f"DeviceReader shadow stoped from dispatcher! name={shadow_name}")

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

class Dispatcher(Shadow):
    def on_configure(self):
        self.add_reflex(DispatcherReflex(autostart=True))

