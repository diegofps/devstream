#!/usr/bin/env python3

from evdev import InputDevice, UInput, AbsInfo, list_devices, ecodes as e
import time

def grab_device():
    devices = [InputDevice(path) for path in list_devices()]
    for d in devices:
        if d.name == "Logitech USB Trackball":
            d.grab()
            return d
    return None

def refine(v):
    v2 = v**2 if v > 0 else -v**2
    a = 0.99
    return int(v * a + v2 * (1-a))

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


class WheelKey:
    def __init__(self, name, device, type, code, code_high, speed):
        self.device = device
        self.speed = speed
        self.name = name
        self.type = type
        self.code = code
        self.code_high = code_high
        self.value = 0
        self.cumulative = 0
    
    def update(self, value):
        if value == self.value:
            return
        
        self.value = value
        value = self.value * self.speed

        self.cumulative += value
        self.device.write(self.type, self.code_high, value)
        
        while self.cumulative >= 120:
            self.device.write(self.type, self.code, 1)
            self.cumulative -= 120

        while self.cumulative <= 0:
            self.device.write(self.type, self.code, -1)
            self.cumulative += 120

        self.device.write(e.EV_SYN, e.SYN_REPORT, 0)
    
cap = {
    e.EV_KEY : [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, e.KEY_TAB, e.KEY_LEFTALT],
    e.EV_REL : [e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_HWHEEL, e.REL_WHEEL_HI_RES, e.REL_HWHEEL_HI_RES]
}

vdev = UInput(cap, name="virtualmarble", version=0x3)

bt_leftalt = Key("leftalt", vdev, e.EV_KEY, e.KEY_LEFTALT)
bt_tab     = Key("tab",     vdev, e.EV_KEY, e.KEY_TAB)
bt_right   = Key("right",   vdev, e.EV_KEY, e.BTN_RIGHT, 90001)
bt_left    = Key("left",    vdev, e.EV_KEY, e.BTN_LEFT, 90004)
bt_middle  = Key("middle",  vdev, e.EV_KEY, e.BTN_MIDDLE, 90005)
bt_rel_x   = Key("rel_x",   vdev, e.EV_REL, e.REL_X)
bt_rel_y   = Key("rel_y",   vdev, e.EV_REL, e.REL_Y)
bt_back    = Key("back",    vdev, e.EV_KEY, e.BTN_SIDE, 90004)
bt_forward = Key("forward", vdev, e.EV_KEY, e.BTN_EXTRA, 90005)
bt_wheel_h = WheelKey("wheel_h", vdev, e.EV_REL, e.REL_HWHEEL, e.REL_HWHEEL_HI_RES, 20)
bt_wheel_v = WheelKey("wheel_v", vdev, e.EV_REL, e.REL_WHEEL, e.REL_WHEEL_HI_RES, 10)

while True:

    dev = grab_device()

    if dev is None:
        print("Trackball not found, waiting for it...")
        time.sleep(3)
        continue
    
    done = False
    
    left_big    = 0
    right_big   = 0
    left_small  = 0
    right_small = 0
    rel_x       = 0
    rel_y       = 0
    tab_state   = False

    for event in dev.read_loop():

        if event.type == e.EV_SYN:
            if event.code == e.SYN_REPORT:

                # Alternate state
                if right_big == 1:
                    bt_right.update(0)
                    bt_left.update(0)
                    bt_middle.update(0)
                    bt_rel_x.update(0)
                    bt_rel_y.update(0)
                    bt_back.update(left_big)
                    bt_forward.update(left_small)

                    bt_wheel_h.update(rel_x)
                    bt_wheel_v.update(-rel_y)

                    if not tab_state and right_small == 1:
                        bt_leftalt.update(1)
                        tab_state = True
                    
                    bt_tab.update(right_small)

                # Normal state
                else:
                    bt_left.update(left_big)
                    bt_right.update(left_small)
                    bt_middle.update(right_small)
                    bt_rel_x.update(refine(rel_x))
                    bt_rel_y.update(refine(rel_y))
                    bt_wheel_h.update(0)
                    bt_wheel_v.update(0)
                    bt_back.update(0)
                    bt_forward.update(0)

                    if tab_state:
                        bt_leftalt.update(0)
                        tab_state = False
                
                rel_x = 0
                rel_y = 0

        elif event.type == e.EV_KEY:
            if event.code == e.BTN_LEFT:
                left_big = event.value
                
            elif event.code == e.BTN_RIGHT:
                right_big = event.value

            elif event.code == e.BTN_EXTRA:
                right_small = event.value

            elif event.code == e.BTN_SIDE:
                left_small = event.value
                

        elif event.type == e.EV_REL:
            if event.code == e.REL_X:
                rel_x = event.value

            elif event.code == e.REL_Y:
                rel_y = event.value

