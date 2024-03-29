
from shadows.virtual_pen import TOPIC_VIRTUALPEN_EVENT
from shadows.watch_login import TOPIC_LOGIN_CHANGED
from shadows.virtual_keyboard import OutputEvent
from evdev import ecodes as e
from reflex import Reflex

from threading import Thread
from queue import Queue

import time
import math
import log
import sys
import os

# Configure PIPE
class Canvas(Thread):

    def __init__(self):
        self.pipe_filepath = "/tmp/shadow_xppen_deco_pro"
        self.process_filepath = ["./canvas2.release", "./build-canvas2-Desktop_Qt_6_4_0_GCC_64bit-Debug/canvas2"]
        self.userdisplay = None
        self.username = None
        self.queue = Queue()
        self.tries = 3

        if os.path.exists(self.pipe_filepath):
            # os.unlink(self.pipe_filepath)
            os.chmod(self.pipe_filepath, 0o666)
        else:
            try:
                os.umask(0)
                os.mkfifo(self.pipe_filepath, 0o666)
                os.umask(0o133)
            except FileExistsError:
                pass

        self.process_thread = Thread(target=self.process_main)
        self.pipe_thread = Thread(target=self.pipe_main)

        if self.process_filepath:
            self.process_thread.start()
        self.pipe_thread.start()

    def process_main(self):
        while True:
            if self.username is None or self.userdisplay is None:
                log.warn("Deco Pro is waiting for user interface")
                time.sleep(2)
                continue
            
            # This is where canvas2 will save its log. We touch it here as it will 
            # run as the user will not have access to this folder.
            canvas_log_filepath = "./main.log.qt"
            os.system(f"touch {canvas_log_filepath}")
            os.system(f"chown {self.username}:{self.username} {canvas_log_filepath}")

            # Now we try to execute canvas2 from one of the available paths
            try:
                for filepath in self.process_filepath:
                    if os.path.exists(filepath):
                        cmd = "su %s -c 'DISPLAY=%s %s'" % (self.username, self.userdisplay, filepath)
                        status = os.system(cmd)

                        if status == 2:
                            log.warn("Canvas exited with exit status 2, exiting")
                            os._exit(os.EX_OK)
                        else:
                            log.error("Canvas process finished unexpectedly", status)
                
                log.warn("Failed to start canvas process for xppen deco pro")
            except Exception as e:
                log.error("Failed to start or execute the canvas process, retrying in 5s...", 
                    exception_class=e.__class__.__name__,
                    description=e, 
                )
            time.sleep(5)

    def pipe_main(self):
        while True:
            try:
                with open(self.pipe_filepath, 'a') as fout:
                    while True:
                        msg = self.queue.get()

                        if msg is None:
                            break

                        if not msg[0] == ' ':
                            msg = ' ' + msg
                        
                        if not msg[-1] == ' ':
                            msg = msg + ' '
                        
                        for i in range(self.tries):
                            try:
                                # log.debug("sending command: ", msg)
                                fout.write(msg)
                                fout.flush()
                                # log.debug("message sent")
                                break
                            except Exception as e:
                                log.error("Failed to send message to canvas.", 
                                    attempt=f"{i+1}/{self.tries}", 
                                    msg=msg, 
                                    exception_class=e.__class__.__name__, 
                                    description=e, 
                                )
                                time.sleep(1)
            except Exception as e:
                log.error("Failed to connect to pipe.", 
                    attempt=f"{i+1}/{self.tries}", 
                    msg=msg, 
                    exception_class=e.__class__.__name__,
                    description=e, 
                )
                time.sleep(1)

    def send(self, msg):
        self.queue.put(msg)

canvas = Canvas()

MAX_BRUSH = 15
MIN_BRUSH = 1

MAX_ERASER = 15
MIN_ERASER = 1

MODE_TRANSPARENT = 1
MODE_OPAQUE      = 2
MODE_PASSTHROUGH = 3
MODE_DISABLED    = 4


#####################################################################

REQUIRED_DEVICES = [
    "11 inch PenTablet Mouse",
    "11 inch PenTablet Keyboard",
    "11 inch PenTablet",
]

TOPIC_DECOPRO_EVENT = ["DeviceReader:" + x for x in REQUIRED_DEVICES]
TOPIC_DECOPRO_STATE = "XPPEN_DecoPro:State"

def sdistance(x1, y1, x2, y2):
    dx = abs(x1-x2)
    dy = abs(y1-y2)
    return dx*dx + dy*dy

def distance(x1, y1, x2, y2):
    return math.sqrt(sdistance(x1, y1, x2, y2))


class XPPEN_DecoPro_Base(Reflex):

    def __init__(self, shadow):
        super().__init__(shadow)
        self.configure_states(TOPIC_DECOPRO_STATE, TOPIC_DECOPRO_EVENT)
        self.add_listener(TOPIC_LOGIN_CHANGED, self.on_login_changed)
        self.clear()

        self.last_ABS_X = 0
        self.last_ABS_Y = 0
        self.last_ABS_PRESSURE = 0
        self.last_ABS_TILT_X = 0
        self.last_ABS_TILT_Y = 0

        self.touching = False
        self.erasing = False
        self.touch_x = 0
        self.touch_y = 0
        self.erase_x = 0
        self.erase_y = 0

        self.username = None
        self.userdisplay = None
        

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

        if evt.type == e.EV_KEY:

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
            
        if evt.type == e.EV_MSC:

            if evt.code == e.MSC_SCAN:
                if evt.value == 852034:
                    self.saw_MSC_SCAN_852034 = evt.value
                elif evt.value == 852037:
                    self.saw_MSC_SCAN_852037 = evt.value

        if evt.type == e.EV_REL:

            if evt.code == e.REL_WHEEL:
                self.saw_REL_WHEEL = evt.value
            elif evt.code == e.REL_X:
                self.saw_REL_X = evt.value
            elif evt.code == e.REL_Y:
                self.saw_REL_Y = evt.value
            
        if evt.type == e.EV_SYN:

            if evt.code == e.SYN_REPORT:

                # Pen
                if self.saw_BTN_TOUCH is not None and self.saw_MSC_SCAN_852034 is not None:
                    self.on_pen_btn_touch(self.saw_BTN_TOUCH, self.last_ABS_X, self.last_ABS_Y)
                
                if self.saw_BTN_TOUCH is not None and self.saw_MSC_SCAN_852037 is not None:
                    self.on_pen_btn_high(self.saw_BTN_TOUCH, self.last_ABS_X, self.last_ABS_Y)
                    
                if self.saw_BTN_STYLUS is not None:
                    self.on_pen_btn_low(self.saw_BTN_STYLUS, self.last_ABS_X, self.last_ABS_Y)
                
                if self.saw_BTN_TOOL_PEN is not None:
                    self.on_pen_btn_close(self.saw_BTN_TOOL_PEN)

                if (
                    self.saw_ABS_X is not None or 
                    self.saw_ABS_Y is not None or 
                    self.saw_ABS_PRESSURE is not None or 
                    self.saw_ABS_TILT_X is not None or 
                    self.saw_ABS_TILT_Y is not None
                ):
                    if self.saw_ABS_X is not None:
                        self.last_ABS_X = self.saw_ABS_X
                    if self.saw_ABS_Y is not None:
                        self.last_ABS_Y = self.saw_ABS_Y
                    if self.saw_ABS_PRESSURE is not None:
                        self.last_ABS_PRESSURE  = self.saw_ABS_PRESSURE
                    if self.saw_ABS_TILT_X is not None:
                        self.last_ABS_TILT_X = self.saw_ABS_TILT_X
                    if self.saw_ABS_TILT_Y is not None:
                        self.last_ABS_TILT_Y = self.saw_ABS_TILT_Y
                    
                    self.on_pen_abs(
                        self.last_ABS_X, 
                        self.last_ABS_Y, 
                        self.last_ABS_PRESSURE, 
                        self.last_ABS_TILT_X, 
                        self.last_ABS_TILT_Y,
                    )
                

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
                elif self.saw_N is not None:
                    self.on_key31(self.saw_N)
                
                # Orb
                if self.saw_REL_WHEEL is not None:
                    self.on_orb_wheel(self.saw_REL_WHEEL)
                elif self.saw_REL_X is not None or self.saw_REL_Y is not None:
                    x = 0 if self.saw_REL_X is None else self.saw_REL_X
                    y = 0 if self.saw_REL_Y is None else self.saw_REL_Y
                    self.on_orb_rel(x, y)
                    
                self.clear()
        
    def on_login_changed(self, topic_name, event):
        if len(event) == 0:
            canvas.username, canvas.userdisplay = None, None
        else:
            canvas.username, canvas.userdisplay = event[0]
        log.info("login changed received", self.username, self.userdisplay)

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
        self.saw_ABS_X = None
        self.saw_ABS_Y = None
        self.saw_ABS_PRESSURE = None
        self.saw_ABS_TILT_X = None
        self.saw_ABS_TILT_Y = None
        self.saw_BTN_TOUCH = None
        self.saw_BTN_STYLUS = None
        self.saw_BTN_TOOL_PEN = None
        self.saw_MSC_SCAN_852034 = None
        self.saw_MSC_SCAN_852037 = None

    def on_activate(self):
        self.clear()

    
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
        log.debug("Deco pro key 11", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Disable")
        
    def on_key20(self, value):
        log.debug("Deco pro key 20", value)
        if value == 0:
            canvas.send("change_page -1")
        # Previous page
        
    def on_key21(self, value):
        log.debug("Deco pro key 21", value)
        if value == 0:
            canvas.send("change_page +1")
        # Next page
        
    def on_key30(self, value):
        log.debug("Deco pro key 30", value)
        if value != 1:
            canvas.send("undo -1")
        # UNDO
        
    def on_key31(self, value):
        log.debug("Deco pro key 31", value)
        if value != 1:
            canvas.send("undo +1")
        # REDO
    
    def on_orb_rel(self, rel_x, rel_y):
        # log.debug("Deco pro key orb_rel", rel_x, rel_y)
        canvas.send(f"move_page {rel_x*2} {rel_y*2}")

    def on_orb_wheel(self, value):
        # log.debug("Deco pro key orb_wheel", value)
        canvas.send(f"change_brush_size {value} {self.last_ABS_X} {self.last_ABS_Y}")

    def on_pen_abs(self, x, y, z, tx, ty):
        # log.debug("Deco pro key pen_abs", x, y, z, tx, ty)

        if self.touching and distance(self.touch_x, self.touch_y, x, y) > 10:
            canvas.send(f"draw {self.touch_x} {self.touch_y} {x} {y}")
            self.touch_x = x
            self.touch_y = y
        
        if self.erasing and distance(self.erase_x, self.erase_y, x, y) > 10:

            self.erase_last_x = self.erase_x
            self.erase_last_y = self.erase_y

            self.erase_x = x
            self.erase_y = y

            canvas.send(f"erase {self.erase_start_x} {self.erase_start_y} {self.erase_last_x} {self.erase_last_y} {self.erase_x} {self.erase_y}")
        
        self.last_x = x
        self.last_y = y
        
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.function("ABS", x, y, 0, 0, 0)
    
    def on_pen_btn_close(self, value):
        # log.debug("Deco pro key pen_btn_close", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_TOOL_PEN", self.saw_BTN_TOOL_PEN)

    def on_pen_btn_touch(self, value, x, y):
        log.debug("Deco pro key pen_btn_touch", value)

        if self.erasing:
            return
        
        if self.touching and value == 0:
            canvas.send(f"save_present")

        self.touching = value != 0
        
        if self.touching:
            self.touch_x = x
            self.touch_y = y
            canvas.send(f"draw {x} {y} {x+1} {y+1}")

    def on_pen_btn_low(self, value, x, y):
        log.debug("Deco pro key pen_btn_low", value)
        
        if self.erasing and value == 0:
            canvas.send(f"save_present")

        self.erasing = value != 0

        if self.erasing:
            self.erase_start_x = x
            self.erase_start_y = y

            self.erase_x = x
            self.erase_y = y

            if self.touching:
                canvas.send(f"save_present")
                self.touching = False

            # canvas.send(f"erase {x} {y} {x+1} {y+1}")
        
    def on_pen_btn_high(self, value, x, y):
        log.debug("Deco pro key pen_btn_high", value)
        canvas.send(f"toggle_menu")


class XPPEN_DecoPro_Transparent(XPPEN_DecoPro_Base): # N

    def __init__(self, shadow):
        super().__init__(shadow)

    def on_activate(self):
        super().on_activate()
        log.info("mode transparent")
        canvas.send(f"set_page_mode {MODE_TRANSPARENT}")


class XPPEN_DecoPro_Opaque(XPPEN_DecoPro_Base): # N

    def __init__(self, shadow):
        super().__init__(shadow)
        self.size_brush = 20
        self.size_eraser = 20
    
    def on_activate(self):
        super().on_activate()
        log.info("mode opaque")
        canvas.send(f"set_page_mode {MODE_OPAQUE}")


class XPPEN_DecoPro_Passthrough(XPPEN_DecoPro_Base):

    def __init__(self, shadow):
        super().__init__(shadow)

    # def on_key00(self, value):
    #     # log.debug("Deco pro key 00", value)
    #     if value == 0:
    #         self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Transparent")
        
    # def on_key01(self, value):
    #     # log.debug("Deco pro key 01", value)
    #     if value == 0:
    #         self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Opaque")

    # def on_key10(self, value):
    #     # log.debug("Deco pro key 10", value)
    #     # Pass-through mode on hold
    #     # if value == 0:
    #     #     self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Passthrough")
    #     pass
        
    # def on_key11(self, value):
    #     log.debug("Deco pro key 11", value)
    #     if value == 0:
    #         self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Disable")
        
    # def on_key20(self, value):
    #     log.debug("Deco pro key 20", value)
        
    # def on_key21(self, value):
    #     log.debug("Deco pro key 21", value)
        
    def on_key30(self, value):
        log.debug("Deco pro key 30", value)
        
    def on_key31(self, value):
        log.debug("Deco pro key 31", value)
    
    def on_orb_rel(self, rel_x, rel_y):
        log.debug("Deco pro key orb_rel", rel_x, rel_y)
    
    def on_orb_wheel(self, value):
        log.debug("Deco pro key orb_wheel", value)
    
    def on_pen_abs(self, x, y, z, tx, ty):
        # log.debug("Deco pro key pen_abs", abs_x, abs_y, pressure, tx, ty)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.function("ABS", x, y, z, tx, ty)
    
    def on_pen_btn_close(self, value):
        # log.debug("Deco pro key pen_btn_close", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_TOOL_PEN", self.saw_BTN_TOOL_PEN)

    def on_pen_btn_touch(self, value, x, y):
        # log.debug("Deco pro key pen_btn_touch", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_TOUCH", self.saw_BTN_TOUCH)

    def on_pen_btn_low(self, value, x, y):
        # log.debug("Deco pro key pen_btn_low", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_MIDDLE", self.saw_BTN_STYLUS)

    def on_pen_btn_high(self, value, x, y):
        # log.debug("Deco pro key pen_btn_high", value)
        with OutputEvent(self.mind, TOPIC_VIRTUALPEN_EVENT) as eb:
            eb.update("BTN_RIGHT", self.saw_BTN_TOUCH)

    def on_activate(self):
        super().on_activate()
        log.info("mode passthrough")
        canvas.send(f"set_page_mode {MODE_PASSTHROUGH}")


class XPPEN_DecoPro_Disable(XPPEN_DecoPro_Passthrough):

    def __init__(self, shadow):
        super().__init__(shadow)
    
    def on_activate(self):
        super().on_activate()
        log.info("mode disabled")
        canvas.send(f"set_page_mode {MODE_DISABLED}")


def on_load(shadow):
    XPPEN_DecoPro_Transparent(shadow)
    XPPEN_DecoPro_Opaque(shadow)
    XPPEN_DecoPro_Passthrough(shadow)
    XPPEN_DecoPro_Disable(shadow)

    shadow.require_device(REQUIRED_DEVICES)
    shadow.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Transparent")

