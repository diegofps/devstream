from shadows.watch_devices import TOPIC_DEVICE_CONNECTED, TOPIC_DEVICE_DISCONNECTED
from shadows.watch_login import TOPIC_LOGIN_CHANGED
from shadows.device_reader import DeviceReader
from shadows.watch_windows import WatchWindows

from evdev import InputDevice
from reflex import Reflex
from shadow import Shadow


"""
This class has three responsibilities:
- Monitor newly connected devices and starts the DeviceReader if there is a shadow that has interest on them. (receiving events from WatchDevices)
- Monitor newly removed devices and stop the DeviceReader if it was active. (receiving events from WatchDevices)
- Monitor the user's login state and start / stop the shadow WatchWindows. (receiving events from WatchLogin)
"""
class DispatcherReflex(Reflex):

    def on_configure(self):
        self.device_readers = {}
        self.watch_windows = None

        self.add_listener(TOPIC_DEVICE_DISCONNECTED, self.on_device_disconnected)
        self.add_listener(TOPIC_DEVICE_CONNECTED, self.on_device_connected)
        self.add_listener(TOPIC_LOGIN_CHANGED, self.on_login_changed)

    def on_device_connected(self, topic_name, event):
        self.log.debug(f"Dispatcher received a device connected event, topic_name=\"{topic_name}\", event=\"{event}\"")

        for device_path in event:
            try:
                dev = InputDevice(device_path)

                if dev.name in self.mind.required_devices:
                    self.log.info(f"Device is required, starting DeviceReader for dev.name=\"{dev.name}\"")
                    shadow = DeviceReader(dev=dev, name=f"DeviceReader:{dev.name}")
                    self.mind.add_shadow(shadow)
                    self.device_readers[device_path] = (shadow.name, shadow)
                    self.log.debug(f"DeviceReader started from dispatcher, name=\"{shadow.name}\"")
                else:
                    self.log.info(f"Device is not required, skipping devname=\"{dev.name}\", path=\"{dev.path}\", required_devices=\"{self.mind.required_devices}\"")
            except Exception as e:
                self.log.warn(f"Device reading failure for devpath=\"{device_path}\", error=\"{e}\"")
    
    def on_device_disconnected(self, topic_name, event):
        for device_path in event:
            self.log.info(f"Device disconnected. device_path={device_path}, self.device_readers={self.device_readers}")

            if device_path in self.device_readers:
                shadow_name, _ = self.device_readers[device_path]
                self.log.info(f"Dispatcher is stopping DeviceReader, name=\"{shadow_name}\"")
                self.mind.remove_shadow(shadow_name)
                del self.device_readers[device_path]
            else:
                self.log.debug(f"Dispatcher sees no reason to stop DeviceReader, device_path=\"{device_path}\"")

    def on_login_changed(self, topic_name, event):
        self.log.info(f"Dispatcher has detected a login change, event=\"{event}\"")

        if self.watch_windows is None:
            if len(event) == 0:
                self.log.warn(f"Unexpected login event with empty length. WatchWindows is not active and event=\"{event}\"")
            else:
                username, display = event[0]
                self.log.info(f"User is now identified by username=\"{username}\" and display=\"{display}\". Starting WatchWindows.")
                self.watch_windows = WatchWindows(username, display)
                self.mind.add_shadow(self.watch_windows)

        else:
            if len(event) == 0:
                self.log.info("User is now inactive. Stoping WatchWindows.")
                if self.watch_windows is not None:
                    self.mind.remove_shadow(self.watch_windows.name)
                    self.watch_windows = None
            else:
                self.log.warn(f"Unexpected login event with non-empty length. WatchWindows is active and event=\"{event}\"")


class Dispatcher(Shadow):
    def on_configure(self):
        super().on_configure()
        self.add_reflex(DispatcherReflex, autostart=True)

