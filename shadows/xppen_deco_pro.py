from shadows.device_writer import OutputEvent
from evdev import ecodes as e
from reflex import Reflex

import log
import os


REQUIRED_DEVICES = [
    "11 inch PenTablet Mouse",
    "11 inch PenTablet Keyboard",
    "11 inch PenTablet",
]

TOPIC_DECOPRO_EVENT = ["DeviceReader:" + x for x in REQUIRED_DEVICES]
TOPIC_DECOPRO_STATE = "XPPEN_DecoPro:State"


class XPPEN_DecoPro_Base(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.active = False
        self.configure_states(TOPIC_DECOPRO_STATE, TOPIC_DECOPRO_EVENT)
        self.clear()

    def on_event(self, topic_name, evt):

        if evt.type == e.EV_ABS:

            if evt.code == e.ABS_X:
                self.saw_ABS_X = evt.value
            elif evt.code == e.ABS_Y:
                self.saw_ABS_Y = evt.value
            elif evt.code == e.ABS_PRESSURE:
                self.saw_ABS_PRESSURE = evt.value

        elif evt.type == e.EV_KEY:

            if evt.code == e.BTN_TOUCH:
                self.saw_BTN_TOUCH = evt.value

            elif evt.code == e.BTN_STYLUS:
                self.saw_BTN_STYLUS = evt.value

            elif evt.code == e.KEY_B:
                self.saw_B = evt.value
            elif evt.code == e.KEY_E:
                self.saw_E = evt.value

            elif evt.code == e.KEY_LEFTALT:
                self.saw_ALT = evt.value
            elif evt.code == e.KEY_SPACE:
                self.saw_SPACE = evt.value

            elif evt.code == e.KEY_V:
                self.saw_V = evt.value
            elif evt.code == e.KEY_S:
                self.saw_S = evt.value

            elif evt.code == e.KEY_Z:
                self.saw_Z = evt.value
            elif evt.code == e.KEY_N:
                self.saw_N = evt.value
            
        elif evt.type == e.EV_MSC:

            if evt.code == e.MSC_SCAN:
                self.saw_MSC_SCAN = evt.value

        elif evt.type == e.EV_REL:

            if evt.code == e.REL_WHEEL:
                self.saw_REL_WHEEL = evt.value
            elif evt.code == e.REL_X:
                self.saw_REL_X = evt.value
            elif evt.code == e.REL_Y:
                self.saw_REL_Y = evt.value
            
        elif evt.type == e.EV_SYN:

            if evt.code == e.SYN_REPORT:

                # Pen
                if self.saw_BTN_TOUCH is not None and self.saw_MSC_SCAN == 852034:
                    self.on_pen_btn_touch(self.saw_BTN_TOUCH)
                if self.saw_BTN_TOUCH is not None and self.saw_MSC_SCAN == 852037:
                    self.on_pen_btn_high(self.saw_BTN_TOUCH)
                if self.saw_BTN_STYLUS is not None:
                    self.on_pen_btn_low(self.saw_BTN_STYLUS)
                if self.saw_ABS_X is not None or self.saw_ABS_Y is not None or self.saw_ABS_PRESSURE is not None:
                    x = 0 if self.saw_ABS_X is None else self.saw_ABS_X
                    y = 0 if self.saw_ABS_Y is None else self.saw_ABS_Y
                    z = 0 if self.saw_ABS_PRESSURE is None else self.saw_ABS_PRESSURE
                    self.on_pen_abs(x, y, z)
                

                # Keys
                elif self.saw_B is not None:
                    self.on_key00(self.saw_B)
                elif self.saw_E is not None:
                    self.on_key01(self.saw_E)
                
                elif self.saw_ALT is not None and self.saw_N is None:
                    self.on_key10(self.saw_ALT)
                elif self.saw_SPACE is not None:
                    self.on_key11(self.saw_SPACE)
                
                elif self.saw_V is not None:
                    self.on_key20(self.saw_V)
                elif self.saw_S is not None:
                    self.on_key21(self.saw_S)
                
                elif self.saw_Z is not None:
                    self.on_key30(self.saw_Z)
                elif self.saw_ALT is not None and self.saw_N is not None:
                    self.on_key31(self.saw_N)
                
                # Orb
                elif self.saw_REL_WHEEL is not None:
                    self.on_orb_wheel(self.saw_REL_WHEEL)
                elif self.saw_REL_X is not None or self.saw_REL_Y is not None:
                    x = 0 if self.saw_REL_X is None else self.saw_REL_X
                    y = 0 if self.saw_REL_Y is None else self.saw_REL_Y
                    self.on_orb_rel(x, y)
                    
                self.clear()
        
    def on_activate(self):
        self.clear()

    def clear(self):
        self.saw_B = None
        self.saw_E = None
        self.saw_ALT = None
        self.saw_SPACE = None
        self.saw_V = None
        self.saw_S = None
        self.saw_Z = None
        self.saw_N = None
        self.saw_REL_X = None
        self.saw_REL_Y = None
        self.saw_REL_WHEEL = None
        # self.saw_ABS_X = None
        # self.saw_ABS_Y = None
        self.saw_ABS_PRESSURE = None
        self.saw_BTN_TOUCH = None
        self.saw_BTN_STYLUS = None
        self.saw_MSC_SCAN = None


class XPPEN_DecoPro_N(XPPEN_DecoPro_Base): # N

    def __init__(self, shadow):
        super().__init__(shadow)
    
    def on_key00(self, value):
        log.debug("Deco pro key 00", value)
        
    def on_key01(self, value):
        log.debug("Deco pro key 01", value)
        
    def on_key10(self, value):
        log.debug("Deco pro key 10", value)
        
    def on_key11(self, value):
        log.debug("Deco pro key 11", value)
        
    def on_key20(self, value):
        log.debug("Deco pro key 20", value)
        
    def on_key21(self, value):
        log.debug("Deco pro key 21", value)
        
    def on_key30(self, value):
        log.debug("Deco pro key 30", value)
        
    def on_key31(self, value):
        log.debug("Deco pro key 31", value)
    
    def on_orb_rel(self, rel_x, rel_y):
        log.debug("Deco pro key orb_rel", rel_x, rel_y)

    def on_orb_wheel(self, value):
        log.debug("Deco pro key orb_wheel", value)

    def on_pen_abs(self, abs_x, abs_y, pressure):
        log.debug("Deco pro key pen_abs", abs_x, abs_y, pressure)
    
    def on_pen_btn_touch(self, value):
        log.debug("Deco pro key pen_btn_touch", value)

    def on_pen_btn_low(self, value):
        log.debug("Deco pro key pen_btn_low", value)

    def on_pen_btn_high(self, value):
        log.debug("Deco pro key pen_btn_high", value)


def on_load(shadow):
    os.mkfifo("/tmp/shadow_xppen_deco_pro")
    
    XPPEN_DecoPro_N(shadow)
    shadow.require_device(REQUIRED_DEVICES)
    shadow.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_N")

