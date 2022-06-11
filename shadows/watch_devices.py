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
        self.devices = self.get_devices()
        self.start()

    def run(self):
        self.done = False

        # Notify others
        self.mind.emit(TOPIC_DEVICE_CONNECTED, list(self.devices.values()))

        while not self.done:
            try:
                cmd = shlex.split("inotifywait -m /dev/input/by-id/ -e CREATE -e DELETE")
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

                    if event_name == "CREATE":
                        device_path = self.follow_symlink(deviceid_path)
                        if device_path is not None:
                            self.devices[deviceid_path] = device_path
                            self.mind.emit(TOPIC_DEVICE_CONNECTED, [device_path])
                    
                    elif event_name == "DELETE":
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
        deviceids = ["/dev/input/by-id/" + x for x in os.listdir("/dev/input/by-id/")]
        devices   = [(x, self.follow_symlink(x)) for x in deviceids]
        return { x[0]:x[1] for x in devices if x[1] is not None }
    
    def follow_symlink(self, filepath):

        if ":" in filepath or ".tmp" in filepath:
            return None

        cmd = shlex.split("readlink -f '%s'" % filepath)
        proc = Popen(cmd, stdout=PIPE)
        filepath2 = proc.stdout.readline()[:-1].decode("utf-8")
        return filepath2

        # print("hi", filepath)
        # print("there", filepath2)

        # return filepath2 if filepath2.startswith("/dev/input/event") else None


def on_load(shadow):
    WatchDevices(shadow)

