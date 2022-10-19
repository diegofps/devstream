
from shadows.virtual_pen import TOPIC_VIRTUALPEN_EVENT
from shadows.virtual_keyboard import OutputEvent
from evdev import ecodes as e
from reflex import Reflex

from threading import Thread
from queue import Queue

import errno
import time
import log
import os

# Configure PIPE
class CanvasPipe(Thread):

    def __init__(self):
        super().__init__(target=self.run)
        self.filepath = "/tmp/shadow_xppen_deco_pro"
        self.queue = Queue()
        self.tries = 3
        self.open()
        self.start()

    def open(self):
        # try:
        #     os.mkfifo(self.filepath)
        # except OSError as oe: 
        #     if oe.errno != errno.EEXIST:
        #         raise

        # if os.path.exists(self.filepath):
        #     os.remove(self.filepath)
        
        # os.mkfifo(self.filepath)

        # log.debug("Opening named pipe")
        # log.debug("Named pipe open")
        pass
    
    def run(self):
        while True:
            msg = self.queue.get()

            if msg is None:
                break
            
            for i in range(self.tries):
                try:
                    with open(self.filepath, 'w') as fout:
                        fout.write(msg)
                        fout.write('\n')
                    break
                except Exception as e:
                    log.error("Failed to send message to canvas.", msg=msg, attempt=f"{i+1}/{self.tries}", error=e)
                    time.sleep(1)

    def send(self, msg):
        self.queue.put(msg)

canvas = CanvasPipe()

TOOL_BRUSH = 1
TOOL_ERASER = 2

MAX_BRUSH = 15
MIN_BRUSH = 1

MAX_ERASER = 15
MIN_ERASER = 1

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
        self.passthrough = False
        self.configure_states(TOPIC_DECOPRO_STATE, TOPIC_DECOPRO_EVENT)
        self.clear()

        self.saw_ABS_X = 0
        self.saw_ABS_Y = 0
        self.saw_ABS_PRESSURE = 0
        self.saw_ABS_TILT_X = 0
        self.saw_ABS_TILT_Y = 0

    def on_event(self, topic_name, evt):

        if not evt.code in [e.ABS_TILT_X, e.ABS_TILT_Y, e.ABS_X, e.ABS_Y, e.ABS_PRESSURE]:
            super().on_event(topic_name, evt) 

        if evt.type == e.EV_ABS:

            if evt.code == e.ABS_X:
                self.saw_ABS_X = evt.value
            elif evt.code == e.ABS_Y:
                self.saw_ABS_Y = evt.value
            elif evt.code == e.ABS_TILT_X:
                self.saw_ABS_TILT_X = evt.value
            elif evt.code == e.ABS_TILT_Y:
                self.saw_ABS_TILT_Y = evt.value
            elif evt.code == e.ABS_PRESSURE:
                self.saw_ABS_PRESSURE = evt.value

        elif evt.type == e.EV_KEY:

            if evt.code == e.BTN_TOUCH:
                self.saw_BTN_TOUCH = evt.value

            elif evt.code == e.BTN_STYLUS:
                self.saw_BTN_STYLUS = evt.value

            elif evt.code == e.BTN_TOOL_PEN:
                self.saw_BTN_TOOL_PEN = evt.value


            if evt.code == e.KEY_B:
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
                
                if self.saw_BTN_TOOL_PEN is not None:
                    self.on_pen_btn_close(self.saw_BTN_TOOL_PEN)

                if self.saw_ABS_X is not None or self.saw_ABS_Y is not None or self.saw_ABS_PRESSURE is not None:
                    x  = 0 if self.saw_ABS_X is None else self.saw_ABS_X
                    y  = 0 if self.saw_ABS_Y is None else self.saw_ABS_Y
                    z  = 0 if self.saw_ABS_PRESSURE is None else self.saw_ABS_PRESSURE
                    tx = 0 if self.saw_ABS_TILT_X is None else self.saw_ABS_TILT_X
                    ty = 0 if self.saw_ABS_TILT_Y is None else self.saw_ABS_TILT_Y
                    self.on_pen_abs(x, y, z, tx, ty)
                

                # Keys
                if self.saw_B is not None:
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
                if self.saw_REL_WHEEL is not None:
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
        # self.saw_ABS_PRESSURE = None
        # self.saw_ABS_TILT_X = None
        # self.saw_ABS_TILT_Y = None
        self.saw_BTN_TOUCH = None
        self.saw_BTN_STYLUS = None
        self.saw_BTN_TOOL_PEN = None
        self.saw_MSC_SCAN = None


class XPPEN_DecoPro_Transparent(XPPEN_DecoPro_Base): # N

    def __init__(self, shadow):
        super().__init__(shadow)
        self.tool = TOOL_BRUSH
        self.size_eraser = 4
        self.size_brush = 4
    
    def on_key00(self, value):
        # log.debug("Deco pro key 00", value)
        # if value == 0:
        #     self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Transparent")
        pass
        
    def on_key01(self, value):
        # log.debug("Deco pro key 01", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Opaque")

    def on_key10(self, value):
        # log.debug("Deco pro key 10", value)
        # Pass-through mode on hold
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Passthrough")
        
    def on_key11(self, value):
        log.debug("Deco pro key 11", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Disable")
        
    def on_key20(self, value):
        log.debug("Deco pro key 20", value)
        canvas.send("previous_page")
        # Previous page
        
    def on_key21(self, value):
        log.debug("Deco pro key 21", value)
        canvas.send("next_page")
        # Next page
        
    def on_key30(self, value):
        log.debug("Deco pro key 30", value)
        canvas.send("undo")
        # UNDO
        
    def on_key31(self, value):
        log.debug("Deco pro key 31", value)
        canvas.send("redo")
        # REDO
    
    def on_orb_rel(self, rel_x, rel_y):
        log.debug("Deco pro key orb_rel", rel_x, rel_y)
        canvas.send(f"move {rel_x} {rel_y}")

    def on_orb_wheel(self, value):
        log.debug("Deco pro key orb_wheel", value)
        if self.tool == TOOL_BRUSH:
            self.size_brush += value
            self.size_brush = min(self.size_brush, MAX_BRUSH)
            self.size_brush = max(self.size_brush, MIN_BRUSH)
            size_brush = 1.5 ** self.size_brush
            canvas.send(f"set_brush_size {size_brush}")
        
        elif self.tool == TOOL_ERASER:
            self.size_eraser += value
            self.size_eraser = min(self.size_eraser, MAX_ERASER)
            self.size_eraser = max(self.size_eraser, MIN_ERASER)
            size_eraser = 1.5 ** self.size_eraser
            canvas.send(f"set_eraser_size {size_eraser}")

        else:
            log.error(f"Invalid VirtualPen tool: {self.tool}")

    def on_pen_abs(self, x, y, z, tx, ty):
        # log.debug("Deco pro key pen_abs", abs_x, abs_y, pressure, tx, ty)
        canvas.send(f"set_cursor_position {x} {y} {z} {tx} {ty}")
        self.last_x = x
        self.last_y = y

        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.function("ABS", x, y, 0, 0, 0)
    
    def on_pen_btn_close(self, value):
        # log.debug("Deco pro key pen_btn_close", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_TOOL_PEN", self.saw_BTN_TOOL_PEN)

    def on_pen_btn_touch(self, value):
        log.debug("Deco pro key pen_btn_touch", value)
        canvas.send(f"set_touching {value}")

    def on_pen_btn_low(self, value):
        log.debug("Deco pro key pen_btn_low", value)
        if value == 0:
            self.tool = TOOL_BRUSH
        else:
            self.tool = TOOL_ERASER

    def on_pen_btn_high(self, value):
        log.debug("Deco pro key pen_btn_high", value)
        canvas.send(f"toggle_menu")
        
    def on_activate(self):
        super().on_activate()
        log.info("mode transparent")
        canvas.send(f"canvas_mode_transparent")


class XPPEN_DecoPro_Opaque(XPPEN_DecoPro_Base): # N

    def __init__(self, shadow):
        super().__init__(shadow)
        self.tool = TOOL_BRUSH
        self.size_brush = 20
        self.size_eraser = 20

        #self.pipe = open(PIPE_FILEPATH, 'w')
    
    def on_key00(self, value):
        # log.debug("Deco pro key 00", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Transparent")
        
    def on_key01(self, value):
        # log.debug("Deco pro key 01", value)
        # if value == 0:
        #     self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Opaque")
        pass

    def on_key10(self, value):
        # log.debug("Deco pro key 10", value)
        # Pass-through mode on hold
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Passthrough")
        
    def on_key11(self, value):
        log.debug("Deco pro key 11", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Disable")
        
    def on_key20(self, value):
        log.debug("Deco pro key 20", value)
        # Previous page
        
    def on_key21(self, value):
        log.debug("Deco pro key 21", value)
        # Next page
        
    def on_key30(self, value):
        log.debug("Deco pro key 30", value)
        # UNDO
        
    def on_key31(self, value):
        log.debug("Deco pro key 31", value)
        # REDO
    
    def on_orb_rel(self, rel_x, rel_y):
        log.debug("Deco pro key orb_rel", rel_x, rel_y)
        # TODO: Move the viewport

    def on_orb_wheel(self, value):
        log.debug("Deco pro key orb_wheel", value)
        # TODO: Change brush size

    def on_pen_abs(self, x, y, z, tx, ty):
        # log.debug("Deco pro key pen_abs", abs_x, abs_y, pressure, tx, ty)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.function("ABS", x, y, 0, 0, 0)
    
    def on_pen_btn_close(self, value):
        # log.debug("Deco pro key pen_btn_close", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_TOOL_PEN", self.saw_BTN_TOOL_PEN)

    def on_pen_btn_touch(self, value):
        log.debug("Deco pro key pen_btn_touch", value)
        # TODO: Activate drawing

    def on_pen_btn_low(self, value):
        log.debug("Deco pro key pen_btn_low", value)
        # TODO: Activate eraser

    def on_pen_btn_high(self, value):
        log.debug("Deco pro key pen_btn_high", value)
        # TODO: Open menu

    def on_activate(self):
        super().on_activate()
        log.info("mode opaque")
        canvas.send(f"canvas_mode_opaque")


class XPPEN_DecoPro_Passthrough(XPPEN_DecoPro_Base):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.tool = TOOL_BRUSH
        self.size_brush = 20
        self.size_eraser = 20

        #self.pipe = open(PIPE_FILEPATH, 'w')
    
    def on_key00(self, value):
        # log.debug("Deco pro key 00", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Transparent")
        
    def on_key01(self, value):
        # log.debug("Deco pro key 01", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Opaque")

    def on_key10(self, value):
        # log.debug("Deco pro key 10", value)
        # Pass-through mode on hold
        # if value == 0:
        #     self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Passthrough")
        pass
        
    def on_key11(self, value):
        log.debug("Deco pro key 11", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Disable")
        
    def on_key20(self, value):
        log.debug("Deco pro key 20", value)
        # Previous page
        
    def on_key21(self, value):
        log.debug("Deco pro key 21", value)
        # Next page
        
    def on_key30(self, value):
        log.debug("Deco pro key 30", value)
        # UNDO
        
    def on_key31(self, value):
        log.debug("Deco pro key 31", value)
        # REDO
    
    def on_orb_rel(self, rel_x, rel_y):
        log.debug("Deco pro key orb_rel", rel_x, rel_y)
        # TODO: Move the viewport

    def on_orb_wheel(self, value):
        log.debug("Deco pro key orb_wheel", value)
        # TODO: Change brush size

    def on_pen_abs(self, x, y, z, tx, ty):
        # log.debug("Deco pro key pen_abs", abs_x, abs_y, pressure, tx, ty)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.function("ABS", x, y, z, tx, ty)
    
    def on_pen_btn_close(self, value):
        # log.debug("Deco pro key pen_btn_close", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_TOOL_PEN", self.saw_BTN_TOOL_PEN)

    def on_pen_btn_touch(self, value):
        # log.debug("Deco pro key pen_btn_touch", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_TOUCH", self.saw_BTN_TOUCH)

    def on_pen_btn_low(self, value):
        # log.debug("Deco pro key pen_btn_low", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_MIDDLE", self.saw_BTN_STYLUS)

    def on_pen_btn_high(self, value):
        # log.debug("Deco pro key pen_btn_high", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_RIGHT", self.saw_BTN_TOUCH)

    def on_activate(self):
        super().on_activate()
        log.info("mode passthrough")
        canvas.send(f"canvas_mode_passthrough")


class XPPEN_DecoPro_Disable(XPPEN_DecoPro_Base):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.tool = TOOL_BRUSH
        self.size_brush = 20
        self.size_eraser = 20

        #self.pipe = open(PIPE_FILEPATH, 'w')
    
    def on_key00(self, value):
        # log.debug("Deco pro key 00", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Transparent")
        
    def on_key01(self, value):
        # log.debug("Deco pro key 01", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Opaque")

    def on_key10(self, value):
        # log.debug("Deco pro key 10", value)
        # Pass-through mode on hold
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Passthrough")
        
    def on_key11(self, value):
        # log.debug("Deco pro key 11", value)
        # if value == 0:
        #     self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Disable")
        pass
        
    def on_key20(self, value):
        log.debug("Deco pro key 20", value)
        # Previous page
        
    def on_key21(self, value):
        log.debug("Deco pro key 21", value)
        # Next page
        
    def on_key30(self, value):
        log.debug("Deco pro key 30", value)
        # UNDO
        
    def on_key31(self, value):
        log.debug("Deco pro key 31", value)
        # REDO
    
    def on_orb_rel(self, rel_x, rel_y):
        log.debug("Deco pro key orb_rel", rel_x, rel_y)
        # TODO: Move the viewport

    def on_orb_wheel(self, value):
        log.debug("Deco pro key orb_wheel", value)
        # TODO: Change brush size

    def on_pen_abs(self, x, y, z, tx, ty):
        # log.debug("Deco pro key pen_abs", abs_x, abs_y, pressure, tx, ty)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.function("ABS", x, y, z, tx, ty)
    
    def on_pen_btn_close(self, value):
        # log.debug("Deco pro key pen_btn_close", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_TOOL_PEN", self.saw_BTN_TOOL_PEN)

    def on_pen_btn_touch(self, value):
        # log.debug("Deco pro key pen_btn_touch", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_TOUCH", self.saw_BTN_TOUCH)

    def on_pen_btn_low(self, value):
        # log.debug("Deco pro key pen_btn_low", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_MIDDLE", self.saw_BTN_STYLUS)

    def on_pen_btn_high(self, value):
        # log.debug("Deco pro key pen_btn_high", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_RIGHT", self.saw_BTN_TOUCH)

    def on_activate(self):
        super().on_activate()
        log.info("mode disabled")
        canvas.send(f"canvas_mode_disabled")


def on_load(shadow):
    XPPEN_DecoPro_Transparent(shadow)
    XPPEN_DecoPro_Opaque(shadow)
    XPPEN_DecoPro_Passthrough(shadow)
    XPPEN_DecoPro_Disable(shadow)

    shadow.require_device(REQUIRED_DEVICES)
    shadow.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Transparent")

