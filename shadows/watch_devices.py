from subprocess import Popen, PIPE
from reflex import Reflex

import shlex
import time
import log
import os

TOPIC_DEVICE_CONNECTED = "DeviceConnected"
TOPIC_DEVICE_DISCONNECTED = "DeviceDisconnected"

class WatchDevices2(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)

        self.target_folder = "/dev/input/"
        devices = [os.path.join(self.target_folder, x) for x in os.listdir(self.target_folder)]
        devices = [x for x in devices if not os.path.isdir(x)]
        self.devices = set(devices)
        self.start()

    def run(self):
        self.done = False
        self.mind.emit(TOPIC_DEVICE_CONNECTED, list(self.devices))

        while not self.done:
            try:
                with Popen(shlex.split(f"inotifywait -m {self.target_folder} -e CREATE -e DELETE"), stdout=PIPE, stderr=PIPE) as proc:
                    while True:
                        line = proc.stdout.readline()[:-1].decode("utf-8")
                        
                        if line is None or line == "":
                            error_msg = proc.stderr.readlines()
                            log.error(f"inotifywait returned an empty line, returncode={proc.returncode}, error_msg={error_msg}")
                            break

                        folderpath, event_names, filename = line.split(" ", 2)
                        event_names = event_names.split(',')
                        device = folderpath + filename

                        if "CREATE" in event_names:
                            log.debug("Device created:", device)
                            if not device in self.devices:
                                self.devices.add(device)
                                self.mind.emit(TOPIC_DEVICE_CONNECTED, [device])
                            else:
                                log.error("Device already known")
                        
                        if "DELETE" in event_names:
                            log.debug("Device disconnected:", device)
                            if device in self.devices:
                                self.devices.remove(device)
                                self.mind.emit(TOPIC_DEVICE_DISCONNECTED, [device])
                            else:
                                log.debug(f"ignoring device not tracked: {device}")

            except Exception as e:
                log.error("Fail during device monitoring, retrying in 3s...", e)
            
            time.sleep(3)


def on_load(shadow):
    WatchDevices2(shadow)

