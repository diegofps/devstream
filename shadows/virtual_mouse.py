from evdev import AbsInfo, UInput, ecodes as e
from keys import WheelKey, DirectKey

from .virtual_device import VirtualDevice, VirtualDeviceEvent

import time
import log


TOPIC_VIRTUALMOUSE_EVENT = "VirtualMouse"


class VirtualMouseEvent(VirtualDeviceEvent):
    def __init__(self, mind, source):
        super().__init__(mind, TOPIC_VIRTUALMOUSE_EVENT, source)


class VirtualMouse(VirtualDevice):

    def __init__(self, shadow):
        super().__init__(shadow, "devstream_mouse")
        
        self.init_keys()
        self.add_listener(TOPIC_VIRTUALMOUSE_EVENT, self.on_event)

    def get_capabilities(self):
        return {
            e.EV_KEY : [
                e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, 
            ],

            e.EV_ABS: [
                (e.ABS_X, AbsInfo(value=0, min=0, max=+32767, fuzz=0, flat=0, resolution=0)), 
                (e.ABS_Y, AbsInfo(value=0, min=0, max=+32767, fuzz=0, flat=0, resolution=0)), 
            ],

            e.EV_REL : [
                (e.REL_X, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_Y, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_WHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_HWHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_WHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_HWHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
            ],
            
            e.EV_MSC : [
                e.MSC_SCAN, 
            ]
        }

    def init_keys(self):

        self.ABS_X   = DirectKey("ABS_X",   self.vdev, e.EV_ABS, e.ABS_X)
        self.ABS_Y   = DirectKey("ABS_Y",   self.vdev, e.EV_ABS, e.ABS_Y)
        self.REL_X   = DirectKey("REL_X",   self.vdev, e.EV_REL, e.REL_X)
        self.REL_Y   = DirectKey("REL_Y",   self.vdev, e.EV_REL, e.REL_Y)
        self.WHEEL_H = WheelKey ("WHEEL_H", self.vdev, e.EV_REL, e.REL_HWHEEL, e.REL_HWHEEL_HI_RES, 120)
        self.WHEEL_V = WheelKey ("WHEEL_V", self.vdev, e.EV_REL, e.REL_WHEEL,  e.REL_WHEEL_HI_RES,  120)
    
        self.add_keys([
            ("BTN_RIGHT", 90001), ("BTN_LEFT", 90004), ("BTN_MIDDLE", 90005), ("BTN_SIDE", 90004), ("BTN_EXTRA", 90005), 
        ])
    

def on_load(shadow):
    VirtualMouse(shadow)
