from evdev import ecodes as e
from reflex import Reflex
from keys import Key

import time
import log


class VirtualDeviceEvent:

    PRESS    = 0
    RELEASE  = 1
    UPDATE   = 2
    UPDATE_H = 3
    UPDATE_V = 4
    UNLOCK   = 5
    FORWARD  = 6
    FUNCTION = 7
    SLEEP    = 8
    SEQUENCE = 9

    def __init__(self, mind, topic, source=None):
        self.source   = source
        self.topic    = topic
        self.mind     = mind
        self.sequence = []
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.emit()
    
    def press(self, key_name):
        event = (VirtualDeviceEvent.PRESS, key_name, self.source)
        self.sequence.append(event)

    def release(self, key_name):
        event = (VirtualDeviceEvent.RELEASE, key_name, self.source)
        self.sequence.append(event)

    def update(self, key_name, value):
        event = (VirtualDeviceEvent.UPDATE, key_name, value, self.source)
        self.sequence.append(event)

    def update_h(self, key_name, value):
        event = (VirtualDeviceEvent.UPDATE_H, key_name, value, self.source)
        self.sequence.append(event)

    def update_v(self, key_name, value):
        event = (VirtualDeviceEvent.UPDATE_V, key_name, value, self.source)
        self.sequence.append(event)

    def unlock(self, key_name):
        event = (VirtualDeviceEvent.UNLOCK, key_name, self.source)
        self.sequence.append(event)

    def forward(self, type, code, value):
        event = (VirtualDeviceEvent.FORWARD, type, code, value, self.source)
        self.sequence.append(event)

    def function(self, function_name, *args):
        event = (VirtualDeviceEvent.FUNCTION, self.source, function_name, *args)
        self.sequence.append(event)

    def sleep(self, delay):
        event = (VirtualDeviceEvent.SLEEP, delay, self.source)
        self.sequence.append(event)
    
    def emit(self):
        sequenceLen = len(self.sequence)

        if sequenceLen == 0:
            return
        
        elif sequenceLen == 1:
            self.mind.emit(self.topic, self.sequence[0])

        else:
            event = (VirtualDeviceEvent.SEQUENCE, self.sequence, self.source)
            self.mind.emit(self.topic, event)


class VirtualDevice(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.vdev = None

    def on_event(self, topic_name, event):
        # log.debug("Processing VirtualDevice event", event)
        event_type = event[0]

        if event_type == VirtualDeviceEvent.SEQUENCE:
            for event2 in event[1]:
                self.on_event(topic_name, event2)
        
        elif event_type == VirtualDeviceEvent.PRESS:
            key_name = event[1]

            if hasattr(self, key_name):
                getattr(self, key_name).press()
        
        elif event_type == VirtualDeviceEvent.RELEASE:
            key_name = event[1]

            if hasattr(self, key_name):
                getattr(self, key_name).release()
        
        elif event_type == VirtualDeviceEvent.UPDATE:
            key_name = event[1]
            value = event[2]

            if hasattr(self, key_name):
                getattr(self, key_name).update(value)
        
        elif event_type == VirtualDeviceEvent.UPDATE_H:
            key_name = event[1]
            value = event[2]

            if hasattr(self, key_name):
                getattr(self, key_name).update_h(value)
        
        elif event_type == VirtualDeviceEvent.UPDATE_V:
            key_name = event[1]
            value = event[2]

            if hasattr(self, key_name):
                getattr(self, key_name).update_v(value)
        
        elif event_type == VirtualDeviceEvent.UNLOCK:
            key_name = event[1]
            
            if hasattr(self, key_name):
                getattr(self, key_name).unlock()
        
        elif event_type == VirtualDeviceEvent.FORWARD:
            type  = event[1]
            code  = event[2]
            value = event[3]

            if not code in self.acquired_keys:
                log.info(f"{self.__class__.__name__} is ignoring key {e.KEY[code]}")
            
            self.vdev.write(type, code, value)
        
        elif event_type == VirtualDeviceEvent.FUNCTION:
            function_name = "function_" + event[2]
            
            if hasattr(self, function_name):
                params = event[3:]
                getattr(self, function_name)(*params)
        
        elif event_type == VirtualDeviceEvent.SLEEP:
            delay = event[1]
            time.sleep(delay)
        
        else:
            log.error(f"Invalid event_type in {self.__class__.__name__} event: {event_type}")

    def terminate(self):
        if self.vdev is not None:
            self.vdev.close()

    def add_keys(self, names):
        for name in names:
            if isinstance(name, tuple):
                name, scan_code = name
            else:
                scan_code = None
            
            name = name if name.startswith("KEY_") or name.startswith("BTN_") else "KEY_" + name
            value = getattr(e, name)
            key = Key(name, self.vdev, e.EV_KEY, value, scan_code)
            setattr(self, name, key)

