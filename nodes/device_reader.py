from utils import warn, error, info, debug, BaseNode

import traceback
import time
import sys


class DeviceReader(BaseNode):

    def __init__(self, dev, core):
        super().__init__(core)

        self.done = False
        self.core = core
        self.dev = dev

        self.dev.grab()
        self.start()
    
    def run(self):
        while not self.done:
            try:
                if self.dev is None:
                    warn(self.dev.name, "not found, retrying in 3s")
                    time.sleep(3)
                
                else:
                    info("Listening to", self.dev.name, "at", self.dev.path)

                    for event in self.dev.read_loop():
                        self.emit(self.name, event)
                
            except OSError as e:
                error("OSError, resuming in 3s -", e)

                traceback.print_exc(file=sys.stdout)
                time.sleep(3)
            
            except KeyboardInterrupt:
                info("Received a KeyboardInterrupt, terminating app")
        
        if self.dev is not None:
            self.dev.close()

