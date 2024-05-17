from evdev import AbsInfo, UInput, ecodes as e
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
        self.source        = source
        self.topic         = topic
        self.mind          = mind
        self.sequence      = []
    
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

    def sleep(self, delay_in_seconds):
        event = (VirtualDeviceEvent.SLEEP, delay_in_seconds, self.source)
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

    def __init__(self, shadow, name=None, version=0x3, product=0x1, vendor=0x1, input_props=None, bustype=0x3):
        super().__init__(shadow)
        self.functions = {}

        cap = self.get_capabilities()

        if name is not None:
            self.vdev = UInput(cap, name=name, version=version, product=product, vendor=vendor, input_props=input_props, bustype=bustype)
        else:
            self.vdev = None

        self.acquired_keys = set()
        self.acquired_keys.update(cap[1])
        self.acquired_keys.update([x[0] for x in cap[2]])
        self.acquired_keys.update([x[0] for x in cap[3]])

        self._ignored_keys = set()

    def get_capabilities(self):
        return { e.EV_KEY : [], e.EV_ABS: [], e.EV_REL : [], e.EV_MSC : [] }

    def on_event(self, topic_name, event):
        event_type = event[0]

        if event_type == VirtualDeviceEvent.SEQUENCE:
            for event2 in event[1]:
                self.on_event(topic_name, event2)
        
        elif event_type == VirtualDeviceEvent.PRESS:
            self.on_event_press(event[1])
        
        elif event_type == VirtualDeviceEvent.RELEASE:
            self.on_event_release(event[1])
            
        elif event_type == VirtualDeviceEvent.UPDATE:
            self.on_event_update(event[1], event[2])
        
        elif event_type == VirtualDeviceEvent.UPDATE_H:
            self.on_event_update_h(event[1], event[2])
        
        elif event_type == VirtualDeviceEvent.UPDATE_V:
            self.on_event_update_v(event[1], event[2])
        
        elif event_type == VirtualDeviceEvent.UNLOCK:
            self.on_event_unlock(event[1])
            
        elif event_type == VirtualDeviceEvent.FORWARD:
            self.on_event_forward(event[1], event[2], event[3])
        
        elif event_type == VirtualDeviceEvent.FUNCTION:
            self.run(event[2], *event[3:])
        
        elif event_type == VirtualDeviceEvent.SLEEP:
            self.on_event_sleep(event[1])
        
        else:
            log.error(f"Invalid event_type in {self.__class__.__name__} event: {event_type}")

    def on_event_press(self, key_name):
        if hasattr(self, key_name):
            getattr(self, key_name).press()
    
    def on_event_release(self, key_name):
        if hasattr(self, key_name):
            getattr(self, key_name).release()
    
    def on_event_update(self, key_name, value):
        if hasattr(self, key_name):
            getattr(self, key_name).update(value)
    
    def on_event_update_h(self, key_name, value):
        if hasattr(self, key_name):
            getattr(self, key_name).update_h(value)
    
    def on_event_update_v(self, key_name, value):
        if hasattr(self, key_name):
            getattr(self, key_name).update_v(value)
    
    def on_event_unlock(self, key_name):
        if hasattr(self, key_name):
            getattr(self, key_name).unlock()
    
    def on_event_forward(self, type, code, value):
        if not code in self.acquired_keys and not code in self._ignored_keys:
            # log.info(self._ignored_keys, code)
            log.info(f"{self.__class__.__name__} is missing the key {e.KEY[code]}")
        
        self.vdev.write(type, code, value)

    def on_event_sleep(self, delay):
        time.sleep(delay)
        
    def run(self, name, *args):
        getattr(self, 'function_' + name)(*args)

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

    def ignore_keys(self, keys):
        for name in keys:
            name = name if name.startswith("KEY_") or name.startswith("BTN_") else "KEY_" + name
            self._ignored_keys.add(getattr(e, name))
