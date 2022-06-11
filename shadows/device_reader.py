from reflex import Reflex

import time
import log


class DeviceReader(Reflex):

    def __init__(self, shadow, dev):
        super().__init__(shadow, dev.name)

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
                    for event in self.dev.read_loop():
                        self.mind.emit(self.name, event)
                
            except OSError as e:
                log.error("OSError, resuming in 3s -", e)
                # print("Device error", self.dev.name)

                # traceback.print_exc(file=sys.stdout)
                time.sleep(3)
            
            except KeyboardInterrupt:
                log.info("Received a KeyboardInterrupt, terminating app")
        
        if self.dev is not None:
            self.dev.close()
        
        log.debug(self.name, "thread ended. Done =", self.done)

def on_load(shadow, device):
    DeviceReader(shadow, device)
    shadow.name = shadow.name + ":" + device.path
