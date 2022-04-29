from evdev import ecodes as e
import time

class Key:
    
    def __init__(self, name, device, type, code, scan=None):
        self.device = device
        self.scan = scan
        self.name = name
        self.type = type
        self.code = code
        self.value = 0
    
    def update(self, value):
        if value == self.value:
            return
        
        self.value = value

        if self.scan is not None:
            self.device.write(e.EV_MSC, e.MSC_SCAN, self.scan)
        
        self.device.write(self.type, self.code, self.value)
        self.device.write(e.EV_SYN, e.SYN_REPORT, 0)
    
    def press(self):
        self.update(1)
    
    def release(self):
        self.update(0)
    
class DirectKey:
    
    def __init__(self, name, device, type, code, scan=None):
        self.device = device
        self.scan = scan
        self.name = name
        self.type = type
        self.code = code
    
    def update(self, value):
        if self.scan is not None:
            self.device.write(e.EV_MSC, e.MSC_SCAN, self.scan)
        
        self.device.write(self.type, self.code, value)
        self.device.write(e.EV_SYN, e.SYN_REPORT, 0)
    
    def press(self):
        self.update(1)
    
    def release(self):
        self.update(0)
    

class WheelKey:

    def __init__(self, name, device, type, code, code_high, size):
        self.device = device
        self.size = size
        self.name = name
        self.type = type
        self.code = code
        self.code_high = code_high
        self.cumulative = 0
    
    def update(self, value):
        
        self.cumulative += value

        if self.code_high is not None:
            self.device.write(self.type, self.code_high, value)
        
        while self.cumulative >= self.size:
            if self.code is not None:
                self.device.write(self.type, self.code, 1)
            self.cumulative -= self.size

        while self.cumulative <= 0:
            if self.code is not None:
                self.device.write(self.type, self.code, -1)
            self.cumulative += self.size

        self.device.write(e.EV_SYN, e.SYN_REPORT, 0)

class DelayedKey:

    def __init__(self, name, callback, size):
        self.callback = callback
        self.cumulative = 0
        self.last_event = 0
        self.max_delay = 1
        self.upper_size =  size / 2
        self.lower_size = -size / 2
        self.size = size
        self.name = name
    
    def update(self, value):
        current = time.time()

        if current - self.last_event > self.max_delay:
            self.cumulative = value
        else:
            self.cumulative += value

        self.last_event = current

        while self.cumulative >= self.upper_size:
            self.cumulative -= self.upper_size
            self.callback(True)

        while self.cumulative <= self.lower_size:
            self.cumulative -= self.lower_size
            self.callback(False)


class LockableDelayedKey:

    def __init__(self, name, callback_h, callback_v, size):
        self.callback_h = callback_h
        self.callback_v = callback_v
        self.cumulative_h = 0
        self.cumulative_v = 0
        self.last_event = 0
        self.max_delay = 1
        self.upper_size =  size / 2
        self.lower_size = -size / 2
        self.size = size
        self.name = name
        self.lock = None
    
    def update_h(self, value):
        if self.lock is not None and self.lock != "h":
            return
        
        current = time.time()

        if current - self.last_event > self.max_delay:
            self.cumulative_h = value
        else:
            self.cumulative_h += value

        self.last_event = current

        while self.cumulative_h >= self.upper_size:
            self.cumulative_h -= self.upper_size
            self.callback_h(True)
            self.lock = "h"

        while self.cumulative_h <= self.lower_size:
            self.cumulative_h -= self.lower_size
            self.callback_h(False)
            self.lock = "h"
    
    def update_v(self, value):
        if self.lock is not None and self.lock != "v":
            return
        
        current = time.time()

        if current - self.last_event > self.max_delay:
            self.cumulative_v = value
        else:
            self.cumulative_v += value

        self.last_event = current

        while self.cumulative_v >= self.upper_size:
            self.cumulative_v -= self.upper_size
            self.callback_v(True)
            self.lock = "v"

        while self.cumulative_v <= self.lower_size:
            self.cumulative_v -= self.lower_size
            self.callback_v(False)
            self.lock = "v"
    
    def unlock(self):
        self.lock = None

