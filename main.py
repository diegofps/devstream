#!/usr/bin/env python3

from evdev import InputDevice, UInput, AbsInfo, list_devices, ecodes as e
import traceback
import time
import sys

def grab_device():
    devices = [InputDevice(path) for path in list_devices()]
    for d in devices:
        if d.name == "Logitech USB Trackball":
            d.grab()
            return d
    return None

def smooth(v):
    return int(v * 1.5)

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

def process_events(dev):
    global vdev

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

    alt_mode = 0
    tab_mode = 0

    for event in dev.read_loop():
        if event.type == e.EV_KEY:

            # big_left
            if event.code == e.BTN_LEFT:
                if alt_mode == 0:
                    bt_left.update(event.value)
                else:
                    # Activate alt mode if not active
                    if tab_mode != 1:
                        tab_mode = 1
                        bt_leftalt.update(1)
                    
                    # Activate/deactivate tab click
                    bt_tab.update(event.value)

            # small left
            elif event.code == e.BTN_SIDE:
                alt_mode = event.value

                # Disable alternate buttons
                if alt_mode == 0:
                    
                    bt_back.update(0)
                    bt_forward.update(0)

                    bt_leftalt.update(0)
                    bt_tab.update(0)
                    tab_mode = 0

                # Disable normal buttons
                else:
                    bt_left.update(0)
                    bt_right.update(0)
                    bt_middle.update(0)
            
            # small right
            elif event.code == e.BTN_EXTRA:
                if alt_mode == 0:
                    bt_middle.update(event.value)
                else:
                    bt_back.update(event.value)

            # big right
            elif event.code == e.BTN_RIGHT:
                if alt_mode == 0:
                    bt_right.update(event.value)

                else:
                    bt_forward.update(event.value)

        elif event.type == e.EV_REL:

            # Ball rotates horizontally
            if event.code == e.REL_X:
                if alt_mode == 0:
                    bt_rel_x.update(smooth(event.value))
                else:
                    bt_wheel_h.update(event.value)

            # Ball rotates vertically
            elif event.code == e.REL_Y:
                if alt_mode == 0:
                    bt_rel_y.update(smooth(event.value))
                else:
                    bt_wheel_v.update(-event.value)

while True:
    try:
        dev = grab_device()

        if dev is None:
            print("Trackball not found, resuming in 3s")
            time.sleep(3)
        
        else:
            print("Trackball connected")
            process_events(dev)
        
    except OSError:
        print("OSError, resuming in 3s")
        traceback.print_exc(file=sys.stdout)
        time.sleep(3)
    
    except KeyboardInterrupt:
        break

if dev is not None:
    dev.close()

if vdev is not None:
    vdev.close()

print("Bye")
