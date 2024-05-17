
# from shadows.virtual_pen import TOPIC_VIRTUALPEN_EVENT
from shadows.watch_login import TOPIC_LOGIN_CHANGED
from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.virtual_pen import VirtualPenEvent

from evdev import ecodes as e
from reflex import Reflex

from threading import Thread
from queue import Queue

import base64
import time
import math
import log
import sys
import os

TOPIC_NOTIFICATION_CHANGED = "NotificationChanged"

SOURCE_XPPEN_DECO_PRO = "XPPen Deco Pro"

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
                log.warn("DecoPro.Process: Deco Pro is waiting for user interface")
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
                        log.info("DecoPro.Process: Starting Deco Pro Canvas")
                        cmd = "su %s -c 'DISPLAY=%s %s'" % (self.username, self.userdisplay, filepath)
                        status = os.system(cmd)

                        if status == 2:
                            log.warn("DecoPro.Process: Canvas exited with exit status 2, exiting")
                            os._exit(os.EX_OK)
                        else:
                            log.error("DecoPro.Process: Canvas process finished unexpectedly", status)
                
                log.warn("DecoPro.Process: Failed to start canvas process for xppen deco pro")
            except Exception as e:
                log.error("DecoPro.Process: Failed to start or execute the canvas process, retrying in 5s...", 
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
                                log.error("DecoPro.Pipe: Failed to send message to canvas.", 
                                    attempt=f"{i+1}/{self.tries}", 
                                    msg=msg, 
                                    exception_class=e.__class__.__name__, 
                                    description=e, 
                                )
                                time.sleep(1)
            except Exception as e:
                log.error("DecoPro.Pipe: Failed to connect to pipe.", 
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

BIT_BTN_TOUCH_0    = 1 << 0
BIT_BTN_TOUCH_1    = 1 << 1
BIT_BTN_STYLUS_0   = 1 << 2
BIT_BTN_STYLUS_1   = 1 << 3
BIT_BTN_TOOL_PEN_0 = 1 << 4
BIT_BTN_TOOL_PEN_1 = 1 << 5

BIT_KEY_SPACE_0 = 1 << 6
BIT_KEY_SPACE_1 = 1 << 7
BIT_KEY_LEFTALT_0 = 1 << 8
BIT_KEY_LEFTALT_1 = 1 << 9
BIT_KEY_LEFTCTRL_0 = 1 << 10
BIT_KEY_LEFTCTRL_1 = 1 << 11
BIT_KEY_E_0 = 1 << 12
BIT_KEY_E_1 = 1 << 13
BIT_KEY_B_0 = 1 << 14
BIT_KEY_B_1 = 1 << 15
BIT_KEY_V_0 = 1 << 16
BIT_KEY_V_1 = 1 << 17
BIT_KEY_S_0 = 1 << 18
BIT_KEY_S_1 = 1 << 19
BIT_KEY_Z_0 = 1 << 20
BIT_KEY_Z_1 = 1 << 21
BIT_KEY_N_0 = 1 << 22
BIT_KEY_N_1 = 1 << 23

BIT_BTN_0_0 = 1 << 24
BIT_BTN_0_1 = 1 << 25
BIT_BTN_1_0 = 1 << 26
BIT_BTN_1_1 = 1 << 27
BIT_BTN_2_0 = 1 << 28
BIT_BTN_2_1 = 1 << 29
BIT_BTN_3_0 = 1 << 30
BIT_BTN_3_1 = 1 << 31
BIT_BTN_4_0 = 1 << 32
BIT_BTN_4_1 = 1 << 33
BIT_BTN_5_0 = 1 << 34
BIT_BTN_5_1 = 1 << 35
BIT_BTN_6_0 = 1 << 36
BIT_BTN_6_1 = 1 << 37
BIT_BTN_7_0 = 1 << 38
BIT_BTN_7_1 = 1 << 39

BIT_MSC_SCAN_700e0 = 1 << 40
BIT_MSC_SCAN_700e2 = 1 << 41
BIT_MSC_SCAN_70011 = 1 << 42
BIT_MSC_SCAN_70016 = 1 << 43
BIT_MSC_SCAN_70019 = 1 << 44
BIT_MSC_SCAN_70005 = 1 << 45
BIT_MSC_SCAN_70008 = 1 << 46
BIT_MSC_SCAN_d0042 = 1 << 47
BIT_MSC_SCAN_d0044 = 1 << 48

BIT_BTN_STYLUS2_0   = 1 << 49
BIT_BTN_STYLUS2_1   = 1 << 50

BIT_MSC_SCAN_d0045 = 1 << 51
BIT_BTN_TOOL_RUBBER_0 = 1 << 52
BIT_BTN_TOOL_RUBBER_1 = 1 << 53

#####################################################################

REQUIRED_DEVICES = [
    "11 inch PenTablet Mouse",
    "11 inch PenTablet Pad",
    "11 inch PenTablet Pen",
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
        self.add_listener(TOPIC_NOTIFICATION_CHANGED, self.on_notification_changed)
        self.clear()

        self.notificationQueue = []

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

        self.pattern_match_pos = {

            140737488355330:(self.on_pen_btn_touch, 1),
            140737488355329:(self.on_pen_btn_touch, 0),

            281474976710696:(self.on_pen_btn_low, 1),
            281474976710664:(self.on_pen_btn_low, 1),
            281474976710660:(self.on_pen_btn_low, 0),

            422212465065994:(self.on_pen_btn_high, 1),
            11258999068426242:(self.on_pen_btn_high, 1),
            422212465065989:(self.on_pen_btn_high, 0),
            2251799813685249:(self.on_pen_btn_high, 0),
            140737488355345:(self.on_pen_btn_high, 0),
            2533274790395913:(self.on_pen_btn_high, 0),
            4503599627370496:(None, 1), # This is a second release event for the upper button (using the rubber button)
        }

        self.pattern_match = {

            # 32:(self.on_pen_btn_close, 1),
            # 16:(self.on_pen_btn_close, 0),

            # Keys
            35184372121600:(self.on_key00, 1),
            35184372105216:(self.on_key00, 0),

            70368744185856:(self.on_key01, 1),
            70368744181760:(self.on_key01, 0),
            
            2199023256064:(self.on_key10, 1),
            2199023255808:(self.on_key10, 0),
            
            128:(self.on_key11, 1),
            64:(self.on_key11, 0),
            
            17592186175488:(self.on_key20, 1),
            17592186109952:(self.on_key20, 0),
            
            9895605176320:(self.on_key21, 1),
            9895604913152:(self.on_key21, 0),
            
            1099513726976:(self.on_key30, 1),
            1099512677376:(self.on_key30, 0),
            
            7696589785600:(self.on_key31, 1),
            7696585590016:(self.on_key31, 0),
        }
        

    def on_event(self, topic_name, evt):
        # super().on_event(topic_name, evt)

        # log.debug("name:", topic_name, "evt:", evt)

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
                self.saw_pattern |=  BIT_BTN_TOUCH_1 if evt.value else BIT_BTN_TOUCH_0
            elif evt.code == e.BTN_STYLUS:
                self.saw_pattern |=  BIT_BTN_STYLUS_1 if evt.value else BIT_BTN_STYLUS_0
            elif evt.code == e.BTN_STYLUS2:
                self.saw_pattern |=  BIT_BTN_STYLUS2_1 if evt.value else BIT_BTN_STYLUS2_0
            elif evt.code == e.BTN_TOOL_PEN:
                self.saw_BTN_TOOL_PEN = evt.value
                self.saw_pattern |=  BIT_BTN_TOOL_PEN_1 if evt.value else BIT_BTN_TOOL_PEN_0
            elif evt.code == e.BTN_TOOL_RUBBER:
                self.saw_pattern |=  BIT_BTN_TOOL_RUBBER_1 if evt.value else BIT_BTN_TOOL_RUBBER_0

            elif evt.code == e.BTN_0:
                self.saw_pattern |=  BIT_BTN_0_1 if evt.value else BIT_BTN_0_0
            elif evt.code == e.BTN_1:
                self.saw_pattern |=  BIT_BTN_1_1 if evt.value else BIT_BTN_1_0
            elif evt.code == e.BTN_2:
                self.saw_pattern |=  BIT_BTN_2_1 if evt.value else BIT_BTN_2_0
            elif evt.code == e.BTN_3:
                self.saw_pattern |=  BIT_BTN_3_1 if evt.value else BIT_BTN_3_0
            elif evt.code == e.BTN_4:
                self.saw_pattern |=  BIT_BTN_4_1 if evt.value else BIT_BTN_4_0
            elif evt.code == e.BTN_5:
                self.saw_pattern |=  BIT_BTN_5_1 if evt.value else BIT_BTN_5_0
            elif evt.code == e.BTN_6:
                self.saw_pattern |=  BIT_BTN_6_1 if evt.value else BIT_BTN_6_0
            elif evt.code == e.BTN_7:
                self.saw_pattern |=  BIT_BTN_7_1 if evt.value else BIT_BTN_7_0
            
            elif evt.code == e.KEY_SPACE:
                self.saw_pattern |=  BIT_KEY_SPACE_1 if evt.value else BIT_KEY_SPACE_0
            elif evt.code == e.KEY_LEFTALT:
                self.saw_pattern |=  BIT_KEY_LEFTALT_1 if evt.value else BIT_KEY_LEFTALT_0
            elif evt.code == e.KEY_LEFTCTRL:
                self.saw_pattern |=  BIT_KEY_LEFTCTRL_1 if evt.value else BIT_KEY_LEFTCTRL_0
            elif evt.code == e.KEY_E:
                self.saw_pattern |=  BIT_KEY_E_1 if evt.value else BIT_KEY_E_0
            elif evt.code == e.KEY_B:
                self.saw_pattern |=  BIT_KEY_B_1 if evt.value else BIT_KEY_B_0
            elif evt.code == e.KEY_V:
                self.saw_pattern |=  BIT_KEY_V_1 if evt.value else BIT_KEY_V_0
            elif evt.code == e.KEY_S:
                self.saw_pattern |=  BIT_KEY_S_1 if evt.value else BIT_KEY_S_0
            elif evt.code == e.KEY_Z:
                self.saw_pattern |=  BIT_KEY_Z_1 if evt.value else BIT_KEY_Z_0
            elif evt.code == e.KEY_N:
                self.saw_pattern |=  BIT_KEY_N_1 if evt.value else BIT_KEY_N_0
            
            elif isinstance(evt.code, list):
                if e.BTN_0 in evt.code:
                    self.saw_pattern |=  BIT_BTN_0_1 if evt.value else BIT_BTN_0_0
            

        if evt.type == e.EV_MSC:

            if evt.code == e.MSC_SCAN:

                if evt.value == 0x700e0:
                    self.saw_pattern |= BIT_MSC_SCAN_700e0
                elif evt.value == 0x700e2:
                    self.saw_pattern |= BIT_MSC_SCAN_700e2
                elif evt.value == 0x70011:
                    self.saw_pattern |= BIT_MSC_SCAN_70011
                elif evt.value == 0x70016:
                    self.saw_pattern |= BIT_MSC_SCAN_70016
                elif evt.value == 0x70019:
                    self.saw_pattern |= BIT_MSC_SCAN_70019
                elif evt.value == 0x70005:
                    self.saw_pattern |= BIT_MSC_SCAN_70005
                elif evt.value == 0x70008:
                    self.saw_pattern |= BIT_MSC_SCAN_70008
                elif evt.value == 0xd0042:
                    self.saw_pattern |= BIT_MSC_SCAN_d0042
                elif evt.value == 0xd0044:
                    self.saw_pattern |= BIT_MSC_SCAN_d0044
                elif evt.value == 0xd0045:
                    self.saw_pattern |= BIT_MSC_SCAN_d0045

        if evt.type == e.EV_REL:

            if evt.code == e.REL_WHEEL:
                self.saw_REL_WHEEL = evt.value
            elif evt.code == e.REL_X:
                self.saw_REL_X = evt.value
            elif evt.code == e.REL_Y:
                self.saw_REL_Y = evt.value
            
        if evt.type == e.EV_SYN:

            if evt.code == e.SYN_REPORT:

                if (
                    self.saw_ABS_X is not None or 
                    self.saw_ABS_Y is not None or 
                    self.saw_ABS_PRESSURE is not None or 
                    self.saw_ABS_TILT_X is not None or 
                    self.saw_ABS_TILT_Y is not None
                ):
                    if self.saw_ABS_X is not None:
                        self.last_ABS_X = int(self.saw_ABS_X) # int(self.saw_ABS_X / 55798 * 32767)
                    if self.saw_ABS_Y is not None:
                        self.last_ABS_Y = int(self.saw_ABS_Y) # int(self.saw_ABS_Y / 31399 * 32767)
                    if self.saw_ABS_PRESSURE is not None:
                        self.last_ABS_PRESSURE = self.saw_ABS_PRESSURE
                    if self.saw_ABS_TILT_X is not None:
                        self.last_ABS_TILT_X = self.saw_ABS_TILT_X
                    if self.saw_ABS_TILT_Y is not None:
                        self.last_ABS_TILT_Y = self.saw_ABS_TILT_Y
                    
                    # log.debug("Calling on_pen_abs")
                    # MAX_X = 55798 # 32767
                    # MAX_Y = 31399 # 32767

                    self.on_pen_abs(
                        self.last_ABS_X, 
                        self.last_ABS_Y, 
                        self.last_ABS_PRESSURE, 
                        self.last_ABS_TILT_X, 
                        self.last_ABS_TILT_Y, 
                    )
                
                any_match = False

                match = self.pattern_match.get(self.saw_pattern)

                if match is not None:
                    if match[0] is not None:
                        match[0](match[1])
                    any_match = True
                
                match = self.pattern_match_pos.get(self.saw_pattern)

                if match is not None:
                    if match[0] is not None:
                        match[0](match[1], self.last_ABS_X, self.last_ABS_Y)
                    any_match = True
                
                if self.saw_pattern != 0 and not any_match:
                    log.debug(f"Unknown deco pro key pattern: {self.saw_pattern}")

                # Close
                if self.saw_BTN_TOOL_PEN is not None:
                    self.on_pen_btn_close(self.saw_BTN_TOOL_PEN)
                
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
        log.info("Login changed received", self.username, self.userdisplay)

    def on_notification_changed(self, topic_name, event):
        log.info("Processing notification changed event:", event)

        if len(event) == 0 or len(event[0]) != 2:
            log.warn("Invalid notification changed event: ", event)
            return

        message, state = event[0]

        for i,n in enumerate(self.notificationQueue):
            if n[0] == message:
                if state is None:
                    del self.notificationQueue[i]
                else:
                    n[1] = state
                break
        else:
            self.notificationQueue.append([message, state])
        
        notificationBase64 = base64.encode('\n'.join([x[0] for x in self.notificationQueue]))
        canvas.send("set_notification " + notificationBase64)
        
    def clear(self):

        # Touchpad
        self.saw_REL_X = None
        self.saw_REL_Y = None

        # Dial
        self.saw_REL_WHEEL = None

        # Pen
        self.saw_ABS_X = None
        self.saw_ABS_Y = None
        self.saw_ABS_PRESSURE = None
        self.saw_ABS_TILT_X = None
        self.saw_ABS_TILT_Y = None
        self.saw_BTN_TOOL_PEN = None

        # Buttons and Keys
        self.saw_pattern = 0

    def on_activate(self):
        self.clear()

    
    def on_key00(self, value):
        log.debug("Deco pro key 00", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Transparent")
        
    def on_key01(self, value):
        log.debug("Deco pro key 01", value)
        if value == 0:
            self.mind.emit(TOPIC_DECOPRO_STATE, "XPPEN_DecoPro_Opaque")

    def on_key10(self, value):
        log.debug("Deco pro key 10", value)
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
        # log.debug("Base: Deco pro key on_pen_abs", x, y, z, tx, ty, self.touching)

        # log.debug("Dispatching update")
        with VirtualPenEvent(self.mind, SOURCE_XPPEN_DECO_PRO) as eb:
            eb.function("ABS", x, y, 0, 0, 0)
    
        if self.touching and distance(self.touch_x, self.touch_y, x, y) > 10:
            canvas.send(f"draw {self.touch_x} {self.touch_y} {x} {y}")
            self.touch_x = x
            self.touch_y = y
        
        # log.debug("Checking erase")

        if self.erasing and distance(self.erase_x, self.erase_y, x, y) > 10:

            self.erase_last_x = self.erase_x
            self.erase_last_y = self.erase_y

            self.erase_x = x
            self.erase_y = y

            canvas.send(f"erase {self.erase_start_x} {self.erase_start_y} {self.erase_last_x} {self.erase_last_y} {self.erase_x} {self.erase_y}")
        
        self.last_x = x
        self.last_y = y
        
    def on_pen_btn_close(self, value):
        if value == 0:
            return
        
        log.debug("Base: Deco pro key pen_btn_close", value)

        with VirtualPenEvent(self.mind, SOURCE_XPPEN_DECO_PRO) as eb:
            eb.update("BTN_TOOL_PEN", value)

    def on_pen_btn_touch(self, value, x, y):
        log.debug("Base: Deco pro key pen_btn_touch", value)

        if self.erasing:
            return
        
        if self.touching and value == 0:
            canvas.send("save_present")

        self.touching = value != 0
        
        if self.touching:
            self.touch_x = x
            self.touch_y = y
            canvas.send(f"draw {x} {y} {x+1} {y+1}")

    def on_pen_btn_low(self, value, x, y):
        log.debug("Base: Deco pro key pen_btn_low", value)
        
        if self.erasing and value == 0:
            canvas.send("save_present")

        self.erasing = value != 0

        if self.erasing:
            self.erase_start_x = x
            self.erase_start_y = y

            self.erase_x = x
            self.erase_y = y

            if self.touching:
                canvas.send("save_present")
                self.touching = False

            # canvas.send(f"erase {x} {y} {x+1} {y+1}")
        
    def on_pen_btn_high(self, value, x, y):
        log.debug("Base: Deco pro key pen_btn_high", value)
        # canvas.send(f"toggle_menu")


class XPPEN_DecoPro_Transparent(XPPEN_DecoPro_Base): # N

    def __init__(self, shadow):
        super().__init__(shadow)

    def on_activate(self):
        super().on_activate()
        log.info("Transparent: on_activate")
        canvas.send(f"set_page_mode {MODE_TRANSPARENT}")


class XPPEN_DecoPro_Opaque(XPPEN_DecoPro_Base): # N

    def __init__(self, shadow):
        super().__init__(shadow)
        self.size_brush = 20
        self.size_eraser = 20
    
    def on_activate(self):
        super().on_activate()
        log.info("Opaque: on_activate")
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
        log.debug("Passthrough: Deco pro key 30", value)
        
    def on_key31(self, value):
        log.debug("Passthrough: Deco pro key 31", value)
    
    def on_orb_rel(self, rel_x, rel_y):
        log.debug("Passthrough: Deco pro key orb_rel", rel_x, rel_y)
    
    def on_orb_wheel(self, value):
        log.debug("Passthrough: Deco pro key orb_wheel", value)
    
    def on_pen_abs(self, x, y, z, tx, ty):
        # log.debug("Passthrough: Deco pro key on_pen_abs", x, y, z, tx, ty)
        with VirtualPenEvent(self.mind, SOURCE_XPPEN_DECO_PRO) as eb:
            eb.function("ABS", x, y, z, tx, ty)
    
    def on_pen_btn_close(self, value):
        log.debug("Passthrough: Deco pro key pen_btn_close", value)
        with VirtualPenEvent(self.mind, SOURCE_XPPEN_DECO_PRO) as eb:
            eb.update("BTN_TOOL_PEN", value)

    def on_pen_btn_touch(self, value, x, y):
        log.debug("Passthrough: Deco pro key pen_btn_touch", value)
        with VirtualPenEvent(self.mind, SOURCE_XPPEN_DECO_PRO) as eb:
            eb.update("BTN_TOUCH", value)

    def on_pen_btn_low(self, value, x, y):
        log.debug("Passthrough: Deco pro key pen_btn_low", value)
        with VirtualMouseEvent(self.mind, SOURCE_XPPEN_DECO_PRO) as eb:
            eb.update("ABS_X", x)
            eb.update("ABS_Y", y)
            eb.update("BTN_MIDDLE", value)

    def on_pen_btn_high(self, value, x, y):
        log.debug("Passthrough: Deco pro key pen_btn_high", value)
        
        with VirtualMouseEvent(self.mind, SOURCE_XPPEN_DECO_PRO) as eb:
            eb.update("REL_X", 0)
            eb.update("REL_Y", 0)
            eb.update("BTN_RIGHT", value)

    def on_activate(self):
        super().on_activate()
        log.info("Passthrough: on_activate")
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

