from utils import warn, error, info, debug
from threading import Thread

import traceback
import time
import sys


class DeviceReader(Thread):

    def __init__(self, dev, executor, callback):
        super().__init__(name=dev.name, daemon=True)

        self.executor = executor
        self.callback = callback
        self.done = False
        self.dev = dev

        self.dev.grab()
    
    def run(self):
        while not self.done:
            try:
                if self.dev is None:
                    warn(self.dev.name, "not found, retrying in 3s")
                    time.sleep(3)
                
                else:
                    info("Listening to", self.dev.name, "at", self.dev.path)

                    for event in self.dev.read_loop():
                        try:
                            self.executor.submit(self.callback, self.dev.name, event)
                        except RuntimeError as e:
                            warn("Could not parse event, maybe we are shutting down -", e)
                
            except OSError as e:
                error("OSError, resuming in 3s -", e)

                traceback.print_exc(file=sys.stdout)
                time.sleep(3)
            
            except KeyboardInterrupt:
                info("Received a KeyboardInterrupt, terminating app")
        
        if self.dev is not None:
            self.dev.close()

