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
        self.accumulated = 0.0
        self.device = device
        self.scan = scan
        self.name = name
        self.type = type
        self.code = code
    
    def update(self, value:float):
        self.accumulated += value

        if abs(self.accumulated) < 1.0:
            return
    
        inner_value = int(self.accumulated)
        self.accumulated -= inner_value

        if self.scan is not None:
            if isinstance(self.scan, tuple):
                self.device.write(*self.scan)
            else:
                self.device.write(e.EV_MSC, e.MSC_SCAN, self.scan)
        
        self.device.write(self.type, self.code, inner_value)
        self.device.write(e.EV_SYN, e.SYN_REPORT, 0)

    def press(self):
        self.update(1)
    
    def release(self):
        self.update(0)


class SmoothedKey:
    
    def __init__(self, name, device, type, code, scan=None):
        self.accumulated = 0.0
        self.device = device
        self.scan = scan
        self.name = name
        self.type = type
        self.code = code

        self.window_pos = 0
        self.window_size = 5
        self.window_values = [0.0] * self.window_size
    
    def update(self, value:float):
        self.window_values[self.window_pos] = value
        self.window_pos += 1

        if self.window_pos == self.window_size:
            self.window_pos = 0
        
        self.accumulated += sum(self.window_values) / self.window_size

        if abs(self.accumulated) < 1.0:
            return
    
        inner_value = int(self.accumulated)
        self.accumulated -= inner_value

        if self.scan is not None:
            if isinstance(self.scan, tuple):
                self.device.write(*self.scan)
            else:
                self.device.write(e.EV_MSC, e.MSC_SCAN, self.scan)
        
        self.device.write(self.type, self.code, inner_value)
        self.device.write(e.EV_SYN, e.SYN_REPORT, 0)

    def press(self):
        self.update(1)
    
    def release(self):
        self.update(0)


class WheelKey:

    def __init__(self, name, device, type, code, code_high, size):
        self.code_high = code_high
        self.device = device
        self.cumulative = 0.0
        self.size = size
        self.name = name
        self.type = type
        self.code = code
    
    def update(self, value):
        
        self.cumulative += value

        if self.code_high is not None:
            self.device.write(self.type, self.code_high, int(value))
        
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
        self.upper_size =  size / 2
        self.lower_size = -size / 2
        self.callback = callback
        self.cumulative = 0
        self.last_event = 0
        self.max_delay = 1
        self.size = size
        self.name = name
    
    def update(self, value):
        current = time.time()

        if current - self.last_event > self.max_delay:
            self.cumulative = 0
        
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
        self.callback_h   = callback_h
        self.callback_v   = callback_v
        self.size         = size
        self.name         = name
        self.lock         = None
        self.cumulative_h = 0
        self.cumulative_v = 0
    
    def update_h(self, value):
        if self.lock is not None and self.lock != "h":
            return
        
        energy = abs(value)
        demand = abs(self.cumulative_v)

        demand_left = max(0, demand - energy)
        energy_left = energy - (demand - demand_left)

        self.cumulative_v = demand_left if self.cumulative_v > 0 else -demand_left
        value = energy_left if value > 0 else -energy_left

        self.cumulative_h += value

        upper_threshold = self.size / 4 if self.lock is None else self.size / 2
        lower_threshold = -upper_threshold
        
        while self.cumulative_h >= upper_threshold:
            self.cumulative_h -= upper_threshold
            self.callback_h(True)
            self.lock = "h"

        while self.cumulative_h <= lower_threshold:
            self.cumulative_h -= lower_threshold
            self.callback_h(False)
            self.lock = "h"
    
    def update_v(self, value):
        if self.lock is not None and self.lock != "v":
            return
        
        energy = abs(value)
        demand = abs(self.cumulative_h)

        demand_left = max(0, demand - energy)
        energy_left = energy - (demand - demand_left)

        self.cumulative_h = demand_left if self.cumulative_h > 0 else -demand_left
        value = energy_left if value > 0 else -energy_left

        self.cumulative_v += value

        upper_threshold = self.size / 4 if self.lock is None else self.size / 2
        lower_threshold = -upper_threshold
        
        while self.cumulative_v >= upper_threshold:
            self.cumulative_v -= upper_threshold
            self.callback_v(True)
            self.lock = "v"

        while self.cumulative_v <= lower_threshold:
            self.cumulative_v -= lower_threshold
            self.callback_v(False)
            self.lock = "v"
    
    def unlock(self):
        self.cumulative_v = 0
        self.cumulative_h = 0
        self.lock = None


class AdversarialDelayedKey:

    def __init__(self, name, callback_h, callback_v, size, log):
        self.callback_h   = callback_h
        self.callback_v   = callback_v
        self.size         = size
        self.name         = name
        self.cumulative_h = 0
        self.cumulative_v = 0
        self.log          = log

    def update_h(self, value):
        self.cumulative_h, self.cumulative_v = self._consume1(value, self.cumulative_h, self.cumulative_v)
        self.log.debug(f"update_h is updating values, self.cumulative_v={self.cumulative_v}, self.cumulative_h={self.cumulative_h}, self.size={self.size}, value={value}")

        while self.cumulative_h >= self.size:
            self.log.debug(f"update_h is emitting event, self.cumulative_v={self.cumulative_v}, self.size={self.size}")
            self.callback_h(self.cumulative_h)
            self.cumulative_h -= self.size

        while self.cumulative_h <= -self.size:
            self.log.debug(f"update_h is emitting event, self.cumulative_v={self.cumulative_v}, self.size={self.size}")
            self.callback_h(self.cumulative_h)
            self.cumulative_h += self.size

    def update_v(self, value):
        self.cumulative_v, self.cumulative_h = self._consume1(value, self.cumulative_v, self.cumulative_h)
        self.log.debug(f"update_v is updating values, self.cumulative_v={self.cumulative_v}, self.cumulative_h={self.cumulative_h}, self.size={self.size}, value={value}")

        while self.cumulative_v >= self.size:
            self.log.debug(f"update_v is emitting event, self.cumulative_v={self.cumulative_v}, self.size={self.size}")
            self.callback_v(self.cumulative_v)
            self.cumulative_v -= self.size

        while self.cumulative_v <= -self.size:
            self.log.debug(f"update_v is emitting event, self.cumulative_v={self.cumulative_v}, self.size={self.size}")
            self.callback_v(self.cumulative_v)
            self.cumulative_v += self.size
    
    def _consume1(self, energy, current_acc, other_acc):
        if energy >= 0:
            if other_acc >= 0:
                new_energy, new_other_acc = self._consume2(energy, other_acc)
                current_acc += new_energy
                other_acc    = new_other_acc
            else:
                new_energy, new_other_acc = self._consume2(energy, -other_acc)
                current_acc += new_energy
                other_acc    = -new_other_acc
        else:
            if other_acc >= 0:
                new_energy, new_other_acc = self._consume2(-energy, other_acc)
                current_acc += -new_energy
                other_acc    = new_other_acc
            else:
                new_energy, new_other_acc = self._consume2(-energy, -other_acc)
                current_acc += -new_energy
                other_acc    = -new_other_acc
        return current_acc, other_acc
    
    def _consume2(self, energy, other_acc):
        if energy <= other_acc:
            other_acc -= energy
        else:
            energy -= other_acc
            other_acc = 0
        return energy, other_acc
