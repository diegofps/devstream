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


class WheelKey:

    def __init__(self, name, device, type, code, code_high, size, speed):
        self.device = device
        self.speed = speed
        self.size = size
        self.name = name
        self.type = type
        self.code = code
        self.code_high = code_high
        self.cumulative = 0
    
    def update(self, value):
        
        value *= self.speed
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

    def __init__(self, name, device, callback, size):
        self.callback = callback
        self.device = device
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
            self.cumulative -= self.size
            self.callback(True)

        while self.cumulative <= self.lower_size:
            self.cumulative += self.size
            self.callback(False)

        self.device.write(e.EV_SYN, e.SYN_REPORT, 0)
