from node import Node

import traceback
import time
import sys
import log


class DeviceReader(Node):

    def __init__(self, deploy, dev):
        super().__init__(deploy, dev.name)

        self.done = False
        self.dev = dev

        self.dev.grab()
        self.start()
    
    def run(self):
        self.done = False
        while not self.done:
            try:
                if self.dev is None:
                    log.warn(self.dev.name, "not found, retrying in 3s...")
                    time.sleep(3)
                
                else:
                    log.info("Listening to", self.dev.name, "at", self.dev.path)

                    for event in self.dev.read_loop():
                        self.core.emit(self.name, event)
                
            except OSError as e:
                log.error("OSError, resuming in 3s -", e)

                traceback.print_exc(file=sys.stdout)
                time.sleep(3)
            
            except KeyboardInterrupt:
                log.info("Received a KeyboardInterrupt, terminating app")
        
        if self.dev is not None:
            self.dev.close()

def on_load(deploy, device):
    DeviceReader(deploy, device)
