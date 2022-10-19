from evdev import AbsInfo, UInput, ecodes as e
from shadows.virtual_keyboard import OutputEvent
from keys import Key, WheelKey, DirectKey
from reflex import Reflex

import time
import log


TOPIC_VIRTUALPEN_EVENT = "VirtualPen"


class VirtualPen(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        
        self.init_virtual_device()
        self.init_keys()
        self.add_listener(TOPIC_VIRTUALPEN_EVENT, self.on_event)

    def init_virtual_device(self):

        cap = {
            e.EV_KEY : [
                e.BTN_TOOL_PEN, e.BTN_TOUCH, e.BTN_STYLUS, 
                e.BTN_TOOL_RUBBER, e.BTN_TOOL_MOUSE, e.BTN_STYLUS2,
                e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, 
            ],

            e.EV_ABS: [
                (e.ABS_X, AbsInfo(value=0, min=0, max=+32767, fuzz=0, flat=0, resolution=280)), 
                (e.ABS_Y, AbsInfo(value=0, min=0, max=+32767, fuzz=0, flat=0, resolution=158)), 
                (e.ABS_PRESSURE, AbsInfo(value=0, min=0, max=+8191, fuzz=0, flat=0, resolution=1024)), 
                (e.ABS_TILT_X, AbsInfo(value=0, min=-127, max=+127, fuzz=0, flat=0, resolution=256)), 
                (e.ABS_TILT_Y, AbsInfo(value=0, min=-127, max=+127, fuzz=0, flat=0, resolution=256)), 
            ],

            e.EV_MSC : [
                e.MSC_SCAN, 
            ]
        }

        self.vdev = UInput(cap, name="devstream_pen", version=0x3, input_props=[e.INPUT_PROP_DIRECT])

        self.acquired_keys = set()
        self.acquired_keys.update(cap[e.EV_KEY])
        self.acquired_keys.update([x[0] for x in cap[e.EV_ABS]])
        self.acquired_keys.update(cap[e.EV_MSC])

    def init_keys(self):

        self.ABS_X        = DirectKey("ABS_X",        self.vdev, e.EV_ABS, e.ABS_X       )
        self.ABS_Y        = DirectKey("ABS_Y",        self.vdev, e.EV_ABS, e.ABS_Y       )
        self.ABS_PRESSURE = DirectKey("ABS_PRESSURE", self.vdev, e.EV_ABS, e.ABS_PRESSURE)
        self.ABS_TILT_X   = DirectKey("ABS_TILT_X",   self.vdev, e.EV_ABS, e.ABS_TILT_X  )
        self.ABS_TILT_Y   = DirectKey("ABS_TILT_Y",   self.vdev, e.EV_ABS, e.ABS_TILT_Y  )
        
        self.add_keys([
            "BTN_TOOL_PEN", "BTN_STYLUS", "BTN_TOUCH",
            ("BTN_RIGHT", 90001), ("BTN_LEFT", 90004), ("BTN_MIDDLE", 90005), ("BTN_SIDE", 90004), ("BTN_EXTRA", 90005), 
        ])

    def on_event(self, topic_name, event):
        # log.debug("Processing VirtualPen event", event)
        event_type = event[0]

        if event_type == OutputEvent.SEQUENCE:
            for event2 in event[1]:
                self.on_event(topic_name, event2)
        
        elif event_type == OutputEvent.PRESS:
            key_name = event[1]
            if hasattr(self, key_name):
                getattr(self, key_name).press()
        
        elif event_type == OutputEvent.RELEASE:
            key_name = event[1]
            if hasattr(self, key_name):
                getattr(self, key_name).release()
        
        elif event_type == OutputEvent.UPDATE:
            key_name = event[1]
            value = event[2]
            if hasattr(self, key_name):
                getattr(self, key_name).update(value)
        
        elif event_type == OutputEvent.UPDATE_H:
            key_name = event[1]
            value = event[2]
            if hasattr(self, key_name):
                getattr(self, key_name).update_h(value)
        
        elif event_type == OutputEvent.UPDATE_V:
            key_name = event[1]
            value = event[2]
            if hasattr(self, key_name):
                getattr(self, key_name).update_v(value)
        
        elif event_type == OutputEvent.UNLOCK:
            key_name = event[1]
            if hasattr(self, key_name):
                getattr(self, key_name).unlock()
        
        elif event_type == OutputEvent.FORWARD:
            type = event[1]
            code = event[2]
            value = event[3]

            if not code in self.acquired_keys:
                log.error("Missing key", e.KEY[code])
            
            self.vdev.write(type, code, value)
        
        elif event_type == OutputEvent.FUNCTION:
            function_name = "function_" + event[1]
            
            if hasattr(self, function_name):
                params = event[2:]
                getattr(self, function_name)(*params)
        
        elif event_type == OutputEvent.SLEEP:
            delay = event[1]
            time.sleep(delay)
        
        else:
            log.error("Invalid event_type in VirtualPen event:", event_type)

    def function_ABS(self, x, y, pressure, tilt_x, tilt_y):
        self.vdev.write(e.EV_ABS, e.ABS_X, x)
        self.vdev.write(e.EV_ABS, e.ABS_Y, y)
        self.vdev.write(e.EV_ABS, e.ABS_PRESSURE, pressure)
        self.vdev.write(e.EV_ABS, e.ABS_TILT_X, tilt_x)
        self.vdev.write(e.EV_ABS, e.ABS_TILT_Y, tilt_y)
        self.vdev.write(e.EV_SYN, e.SYN_REPORT, 0)

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


def on_load(shadow):
    VirtualPen(shadow)

