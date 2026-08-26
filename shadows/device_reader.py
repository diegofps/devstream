from reflex import Reflex
from shadow import Shadow

import time
import devstreamlog


class DeviceReaderReflex(Reflex):

    def __init__(self, topic_name, dev, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.topic_name = topic_name
        self.dev = dev

    def on_configure(self):
        self.dev.grab()
        self.require_daemon()
        
    def run(self, daemon):
        while not daemon.done:
            try:
                if self.dev is None:
                    self.log.warn("Dev is None not found, retrying in 3s...")
                    time.sleep(3)
                
                else:
                    for event in self.dev.read_loop():
                        if daemon.done:
                            break

                        # log.debug(f"{self.name} is emiting event {event} in topic {self.topic_name}")
                        self.mind.emit(self.topic_name, event)
                
            except OSError as e:
                self.log.error("OSError, resuming in 3s -", e)
                # print("Device error", self.dev.name)
                # traceback.print_exc(file=sys.stdout)
                time.sleep(3)
            
            except KeyboardInterrupt:
                self.log.info("Received a KeyboardInterrupt, terminating app")
        
        if self.dev is not None:
            self.dev.close()
        
        self.log.debug(f"Reflex {self.name}'s daemon thread is ending, daemon.done={daemon.done}")

class DeviceReader(Shadow):

    def __init__(self, dev, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dev = dev

    def on_configure(self):
        super().on_configure()
        self.add_reflex(DeviceReaderReflex, self.name, self.dev, autostart=True)
