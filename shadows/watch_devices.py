from subprocess import Popen, PIPE
from reflex import Reflex

import shlex
import time
import log
import os


TOPIC_DEVICE_CONNECTED = "DeviceConnected"
TOPIC_DEVICE_DISCONNECTED = "DeviceDisconnected"


class WatchDevices(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.perma_devices, self.devices = self.get_devices()
        self.devices = {x[0]:x[1] for x in self.devices}
        self.start()

    def run(self):
        self.done = False

        # Notify others
        event = self.perma_devices + list(self.devices.values())
        self.mind.emit(TOPIC_DEVICE_CONNECTED, event)

        while not self.done:
            try:
                cmd = shlex.split("inotifywait -m /dev/input/by-id/ -e MOVED_TO -e DELETE")
                # debug("WatchDevices event, cmd:", cmd)
                proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
                
                while True:
                    line = proc.stdout.readline()[:-1].decode("utf-8")
                    # debug("WatchDevices event, line:", line)

                    if line is None or line == "":
                        error_msg = proc.stderr.readlines()
                        log.error("returncode:", str(proc.returncode), "error_msg:", error_msg)
                        break

                    folderpath, event_name, filename = line.split(" ", 2)
                    deviceid_path = folderpath + filename

                    if event_name == "MOVED_TO":
                        log.debug("Device disconnected:", deviceid_path)
                        device_path = self.follow_symlink(deviceid_path)
                        if device_path is not None:
                            # log.error("Broadcasting event for creation of ", device_path)
                            self.devices[deviceid_path] = device_path
                            self.mind.emit(TOPIC_DEVICE_CONNECTED, [device_path])
                        else:
                            log.error("follow_symlink returned a None path")
                    
                    elif event_name == "DELETE":
                        log.debug("Device connected:", deviceid_path)
                        if deviceid_path in self.devices:
                            device_path = self.devices[deviceid_path]
                            del self.devices[deviceid_path]
                            self.mind.emit(TOPIC_DEVICE_DISCONNECTED, [device_path])

                    else:
                        log.warn("Unexpected event during device monitoring:", line)

            except Exception as e:
                log.error("Fail during device monitoring, retrying in 3s...", e)
            
            time.sleep(3)

    def get_devices(self):

        # Devices in "/dev/input/by-id/" referencing a file in "/dev/input/"
        device_ids = ["/dev/input/by-id/" + x for x in os.listdir("/dev/input/by-id/")] if os.path.exists("/dev/input/by-id/") else []
        devices = [(x, self.follow_symlink(x)) for x in device_ids]
        devices = [x for x in devices if x[1] is not None]
        removable_devices = set([x[1] for x in devices])

        # Devices in "/dev/input/" but not referenced in "/dev/input/by-id/"
        perma_devices = ["/dev/input/" + x for x in os.listdir("/dev/input/")]
        perma_devices = [x for x in perma_devices if not os.path.isdir(x) and not x in removable_devices]

        # print("perma_devices", perma_devices)
        # print("devices", devices)

        return perma_devices, devices
    
    def follow_symlink(self, filepath):

        if ":" in filepath or ".tmp" in filepath:
            return None

        cmd = shlex.split("readlink -f '%s'" % filepath)
        proc = Popen(cmd, stdout=PIPE)
        filepath2 = proc.stdout.readline()[:-1].decode("utf-8")
        return filepath2


def on_load(shadow):
    WatchDevices(shadow)

