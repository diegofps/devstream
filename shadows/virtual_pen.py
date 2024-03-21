from evdev import AbsInfo, UInput, ecodes as e
from keys import DirectKey

from .virtual_device import VirtualDevice, VirtualDeviceEvent

import log


TOPIC_VIRTUALPEN_EVENT = "VirtualPen"

MAX_X = 32767
MAX_Y = 32767


class VirtualPenEvent(VirtualDeviceEvent):
    def __init__(self, mind, source):
        super().__init__(mind, TOPIC_VIRTUALPEN_EVENT, source)


class VirtualPen(VirtualDevice):

    def __init__(self, shadow):

        super().__init__(shadow, name="devstream_pen") # , vendor=0x28bd, product=0x904, version=0x100, input_props=[1], bustype=0x11
        
        self.mouse_x = MAX_X / 2
        self.mouse_y = MAX_Y / 2

        self.init_keys()
        self.add_listener(TOPIC_VIRTUALPEN_EVENT, self.on_event)

    def get_capabilities(self):

        return {
            e.EV_KEY : [
                e.BTN_TOOL_PEN, e.BTN_TOUCH, e.BTN_STYLUS, 
                # e.BTN_TOOL_RUBBER, e.BTN_TOOL_MOUSE, e.BTN_STYLUS2, 
                # e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, 
            ],

            e.EV_ABS: [
                (e.ABS_X, AbsInfo(value=0, min=0, max=+MAX_X, fuzz=0, flat=0, resolution=200)), 
                (e.ABS_Y, AbsInfo(value=0, min=0, max=+MAX_Y, fuzz=0, flat=0, resolution=200)), 
                (e.ABS_PRESSURE, AbsInfo(value=0, min=0, max=+8191, fuzz=0, flat=0, resolution=1024)), 
                (e.ABS_TILT_X, AbsInfo(value=0, min=-127, max=+127, fuzz=0, flat=0, resolution=256)), 
                (e.ABS_TILT_Y, AbsInfo(value=0, min=-127, max=+127, fuzz=0, flat=0, resolution=256)), 
            ],

            e.EV_REL : [
            ],

            e.EV_MSC : [
                e.MSC_SCAN, 
            ]
        }

    def init_keys(self):

        self.ABS_X        = DirectKey("ABS_X",        self.vdev, e.EV_ABS, e.ABS_X       )
        self.ABS_Y        = DirectKey("ABS_Y",        self.vdev, e.EV_ABS, e.ABS_Y       )
        self.ABS_PRESSURE = DirectKey("ABS_PRESSURE", self.vdev, e.EV_ABS, e.ABS_PRESSURE)
        self.ABS_TILT_X   = DirectKey("ABS_TILT_X",   self.vdev, e.EV_ABS, e.ABS_TILT_X  )
        self.ABS_TILT_Y   = DirectKey("ABS_TILT_Y",   self.vdev, e.EV_ABS, e.ABS_TILT_Y  )
        
        self.add_keys([
            "BTN_TOOL_PEN", "BTN_STYLUS", "BTN_TOUCH",
            # ("BTN_RIGHT", 90001), ("BTN_LEFT", 90004), ("BTN_MIDDLE", 90005), ("BTN_SIDE", 90004), ("BTN_EXTRA", 90005), 
        ])

    def function_ABS(self, x, y, pressure, tilt_x, tilt_y):

        # log.debug("VirtualPen received an ABS event")

        self.vdev.write(e.EV_ABS, e.ABS_X, x)
        self.vdev.write(e.EV_ABS, e.ABS_Y, y)
        self.vdev.write(e.EV_ABS, e.ABS_PRESSURE, pressure)
        self.vdev.write(e.EV_ABS, e.ABS_TILT_X, tilt_x)
        self.vdev.write(e.EV_ABS, e.ABS_TILT_Y, tilt_y)
        self.vdev.write(e.EV_SYN, e.SYN_REPORT, 0)

    # def on_event_forward(self, type, code, value):

    #     log.debug("VirtualPen::on_event_forward", type, code, value)
    #     return super().on_event_forward(type, code, value)
    
    def on_event_update(self, key_name, value):

        if key_name == "ABS_X":
            self.mouse_x = value

        elif key_name == "ABS_Y":
            self.mouse_y = value

        elif key_name == "REL_X":
            self.mouse_x += value
            self.mouse_x = max(0, min(self.mouse_x, 32767))

            key_name = "ABS_X"
            value = int(self.mouse_x)
        
        elif key_name == "REL_Y":
            self.mouse_y += value
            self.mouse_y = max(0, min(self.mouse_y, 32767))

            key_name = "ABS_Y"
            value = int(self.mouse_y)
        
        return super().on_event_update(key_name, value)


def on_load(shadow):
    VirtualPen(shadow)

