# from this import d
from keys import Key, WheelKey, DirectKey, DelayedKey, LockableDelayedKey
from evdev import list_devices, InputDevice, AbsInfo, UInput, ecodes as e
from concurrent.futures import ThreadPoolExecutor
from threading import Thread


import importlib
import traceback
import logging
import evdev
import time
import sys


logging.basicConfig(
    level=logging.INFO, 
    filename="main.log", 
    filemode="w", 
    format='%(name)s - %(levelname)s - %(message)s' 
)


def debug(*args):
    logging.debug(" ".join([str(x) for x in args]))


def info(*args):
    logging.info(" ".join([str(x) for x in args]))


def warn(*args):
    logging.warn(" ".join([str(x) for x in args]))


def error(*args):
    logging.error(" ".join([str(x) for x in args]))


# def grab_device(name):
#     devices = [InputDevice(path) for path in list_devices()]
#     for d in devices:
#         if d.name == name:
#             d.grab()
#             return d
#     return None


def smooth(v):
    return int(v * 1.5)


class BaseConsumer:

    def __init__(self, core):
        self.core = core

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
    
    def terminate(self):
        # This is not relliable for now, we can't intercept kill events from the service
        pass


class BaseProducer(Thread):

    def __init__(self, dev, executor, callback):
        super().__init__(name=dev.name, daemon=True)

        self.dev_name = dev.name
        self.executor = executor
        self.callback = callback
        self.done = False
        self.dev = dev

        self.dev.grab()
    
    def run(self):
        while not self.done:
            try:
                if self.dev is None:
                    warn(self.dev_name, "not found, retrying in 3s")
                    time.sleep(3)
                
                else:
                    info("Connected to", self.dev_name)

                    for event in self.dev.read_loop():
                        try:
                            self.executor.submit(self.callback, self.dev_name, event)
                        except RuntimeError:
                            warn("Could not parse event, maybe we are shutting down")
                
            except OSError:
                error("OSError, resuming in 3s")
                traceback.print_exc(file=sys.stdout)
                time.sleep(3)
            
            except KeyboardInterrupt:
                break
        
        if self.dev is not None:
            self.dev.close()


class BaseState:

    def __init__(self, core):
        self.core = core

    def on_deactivate(self):
        pass

    def on_activate(self):
        pass


class Context:

    def __init__(self, vdev_name):

        cap = {
            e.EV_KEY : [
                e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE, e.BTN_SIDE, e.BTN_EXTRA, 

                e.KEY_LEFTALT, e.KEY_LEFTCTRL, e.KEY_LEFTSHIFT, e.KEY_LEFTMETA, 
                e.KEY_RIGHTALT, e.KEY_RIGHTCTRL, e.KEY_RIGHTSHIFT, e.KEY_RIGHTMETA, 
                e.KEY_TAB, e.KEY_PAGEUP, e.KEY_PAGEDOWN, e.KEY_PRINT, e.KEY_HOME, e.KEY_END,
                e.KEY_MINUS, e.KEY_EQUAL, e.KEY_ESC, e.KEY_COMMA, e.KEY_SLASH, e.KEY_DOT,
                e.KEY_APOSTROPHE, e.KEY_BACKSLASH, e.KEY_LEFTBRACE, e.KEY_RIGHTBRACE, 
                e.KEY_SEMICOLON, e.KEY_SPACE, e.KEY_CAPSLOCK, e.KEY_GRAVE, e.KEY_SCROLLLOCK,
                e.KEY_SYSRQ, e.KEY_PAUSE, e.KEY_DELETE, e.KEY_INSERT, e.KEY_RO, e.KEY_BACKSPACE,
                e.KEY_LEFT, e.KEY_RIGHT, e.KEY_UP, e.KEY_DOWN, e.KEY_ENTER, e.KEY_102ND,

                e.KEY_0, e.KEY_1, e.KEY_2, e.KEY_3, e.KEY_4, e.KEY_5, e.KEY_6, e.KEY_7, e.KEY_8, e.KEY_9, 

                e.KEY_A, e.KEY_B, e.KEY_C, e.KEY_D, e.KEY_E, e.KEY_F, e.KEY_G, e.KEY_H, e.KEY_I, 
                e.KEY_J, e.KEY_K, e.KEY_L, e.KEY_M, e.KEY_N, e.KEY_O, e.KEY_P, e.KEY_Q, e.KEY_R, 
                e.KEY_S, e.KEY_T, e.KEY_U, e.KEY_V, e.KEY_W, e.KEY_X, e.KEY_Y, e.KEY_Z, 

                e.KEY_F1, e.KEY_F2, e.KEY_F3, e.KEY_F4, e.KEY_F5, e.KEY_F6, 
                e.KEY_F7, e.KEY_F8, e.KEY_F9, e.KEY_F10, e.KEY_F11, e.KEY_F12, 

                e.KEY_PLAYPAUSE, e.KEY_NEXTSONG, e.KEY_PREVIOUSSONG, e.KEY_STOPCD, 
                e.KEY_MUTE, e.KEY_VOLUMEUP, e.KEY_VOLUMEDOWN, e.KEY_PRESENTATION, 

            ],

            e.EV_ABS: [
                (e.ABS_X, AbsInfo(value=0, min=0, max=+16384, fuzz=0, flat=0, resolution=0)), 
                (e.ABS_Y, AbsInfo(value=0, min=0, max=+16384, fuzz=0, flat=0, resolution=0)),
            ],

            e.EV_REL : [
                (e.REL_X, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_Y, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)),
                (e.REL_WHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_HWHEEL, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_WHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)), 
                (e.REL_HWHEEL_HI_RES, AbsInfo(value=0, min=-1024, max=+1024, fuzz=0, flat=0, resolution=0)),
            ]
        }

        self.keys = set()
        self.keys.update(cap[1])
        self.keys.update([x[0] for x in cap[2]])
        self.keys.update([x[0] for x in cap[3]])

        self.vdev = UInput(cap, name=vdev_name, version=0x3)

        self.bt_abs_x   = DirectKey("abs_x",   self.vdev, e.EV_ABS, e.ABS_X)
        self.bt_abs_y   = DirectKey("abs_y",   self.vdev, e.EV_ABS, e.ABS_Y)
        self.bt_rel_x   = DirectKey("rel_x",   self.vdev, e.EV_REL, e.REL_X)
        self.bt_rel_y   = DirectKey("rel_y",   self.vdev, e.EV_REL, e.REL_Y)
        self.bt_wheel_h = WheelKey ("wheel_h", self.vdev, e.EV_REL, e.REL_HWHEEL, e.REL_HWHEEL_HI_RES, 120)
        self.bt_wheel_v = WheelKey ("wheel_v", self.vdev, e.EV_REL, e.REL_WHEEL,  e.REL_WHEEL_HI_RES,  120)

        self.key_volume   = DelayedKey("DELAYED_VOLUME",   self.on_update_volume,  200)
        self.key_tabs     = DelayedKey("DELAYED_CTRLTAB",  self.on_switch_tabs,    500)
        self.key_windows  = DelayedKey("DELAYED_ALTTAB",   self.on_switch_windows, 500)
        self.key_zoom     = DelayedKey("DELAYED_ZOOM",     self.on_switch_zoom,    200)
        self.key_undoredo = DelayedKey("DELAYED_UNDOREDO", self.on_undo_redo,      200)

        self.lockable1 = LockableDelayedKey("lockable1", self.on_switch_windows, self.on_switch_tabs, 800)
        self.lockable2 = LockableDelayedKey("lockable2", self.on_undo_redo, self.on_update_volume, 500)
    
        # self.key_back      = Key("back",      self.vdev, e.EV_KEY, e.BTN_SIDE,  90004)
        # self.key_forward   = Key("forward",   self.vdev, e.EV_KEY, e.BTN_EXTRA, 90005)

        self.add_keys([
            ("BTN_RIGHT", 90001), ("BTN_LEFT", 90004), ("BTN_MIDDLE", 90005), 
            ("BTN_SIDE", 90004), ("BTN_EXTRA", 90005), 
        ])

        self.add_keys([
            "LEFTALT", "LEFTCTRL", "LEFTMETA", "LEFTSHIFT", 
            "RIGHTALT", "RIGHTCTRL", "RIGHTMETA", "RIGHTSHIFT", 
            "TAB", "PAGEDOWN", "PAGEUP", 
        ])

        self.add_keys([
            "PLAYPAUSE", "NEXTSONG", "PREVIOUSSONG", "STOPCD", "MUTE", 
            "VOLUMEUP", "VOLUMEDOWN", "EQUAL", "MINUS", "ESC"
        ])

        self.add_keys([
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
        ])

        self.add_keys([
            "F1", "F2", "F3", "F4", "F5", "F6", 
            "F7", "F8", "F9", "F10", "F11", "F12"
        ])

        self.add_keys([
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", 
            "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", 
            "U", "V", "W", "X", "Y", "Z"
        ])

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
    
    def on_undo_redo(self, value):
        if value:
            self.KEY_LEFTCTRL.press()
            self.KEY_LEFTSHIFT.press()
            self.KEY_Z.press()
            self.KEY_Z.release()
            self.KEY_LEFTSHIFT.release()
            self.KEY_LEFTCTRL.release()

        else:
            self.KEY_LEFTCTRL.press()
            self.KEY_Z.press()
            self.KEY_Z.release()
            self.KEY_LEFTCTRL.release()
    
    def on_switch_zoom(self, value):
        if value:
            self.KEY_LEFTCTRL.press()
            self.KEY_EQUAL.press()
            self.KEY_EQUAL.release()
            self.KEY_LEFTCTRL.release()

        else:
            self.KEY_LEFTCTRL.press()
            self.KEY_MINUS.press()
            self.KEY_MINUS.release()
            self.KEY_LEFTCTRL.release()
    
    def on_switch_tabs(self, value):
        if value:
            self.KEY_LEFTCTRL.press()
            self.KEY_LEFTSHIFT.press()
            self.KEY_TAB.press()
            self.KEY_TAB.release()
            self.KEY_LEFTSHIFT.release()
            self.KEY_LEFTCTRL.release()

        else:
            self.KEY_LEFTCTRL.press()
            self.KEY_TAB.press()
            self.KEY_TAB.release()
            self.KEY_LEFTCTRL.release()
    
    def on_switch_windows(self, value):
        self.KEY_LEFTALT.press()
        
        if value:
            self.KEY_TAB.press()
            self.KEY_TAB.release()

        else:
            self.KEY_LEFTSHIFT.press()
            self.KEY_TAB.press()
            self.KEY_TAB.release()
            self.KEY_LEFTSHIFT.release()
    
    def on_update_volume(self, value):
        if value:
            self.KEY_VOLUMEUP.press()
            self.KEY_VOLUMEUP.release()

        else:
            self.KEY_VOLUMEDOWN.press()
            self.KEY_VOLUMEDOWN.release()

    def forward(self, event):
        if not event.code in self.keys:
            error("Missing key", e.KEY[event.code])
        self.vdev.write(event.type, event.code, event.value)

    def close(self):
        if self.vdev is not None:
            self.vdev.close()


class Core:

    def __init__(self):

        self.out = Context("devstream")
        self.consumers = {}
        self.listeners = {}
        self.producers = []
        
        self.devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self.device_names = set([dev.name for dev in self.devices])

        self.load_device_consumer("marble")
        self.load_device_consumer("mx2s")
        self.load_device_consumer("vostrokbd")
    
    def load_device_consumer(self, name):
        mod = importlib.import_module(name)
        mod.on_init(self)

    def add_consumer(self, consumer_name, consumer):
        self.consumers[consumer_name] = consumer
    
    def set_consumer(self, device_name, consumer_name):
        
        if isinstance(device_name, list):
            for name in device_name:
                self.set_consumer(name, consumer_name)
            return

        if not consumer_name in self.consumers:
            print("Can't set consumer. Unknown consumer with name", consumer_name)
            return
        
        if not device_name in self.device_names:
            print("Ignoring listener for missing device", device_name)
            return

        if device_name in self.listeners:
            self.listeners[device_name].on_deactivate()
        
        consumer = self.consumers[consumer_name]
        self.listeners[device_name] = consumer
        consumer.on_activate()

        return consumer

    def start(self):
        
        with ThreadPoolExecutor(max_workers=1) as executor:

            # Start all producers
            # for filter_name in self.listeners.keys():
            #     producer = BaseProducer(filter_name, executor, self.process_event)
            #     self.producers.append(producer)
            #     producer.start()
            
            devices = [InputDevice(path) for path in list_devices()]
            for d in devices:
                if d.name in self.listeners:
                    producer = BaseProducer(d, executor, self.process_event)
                    self.producers.append(producer)
                    producer.start()

            try:
                while True:
                    time.sleep(10000)
                    # print("Leaving in 4s...")
                    # time.sleep(4)
                    # break
            except:
                pass
        
        self.out.close()

        for consumer in self.consumers.values():
            consumer.terminate()

        print("Bye!")

    def process_event(self, device_name, event):
        if device_name in self.listeners:
            self.listeners[device_name].on_event(device_name, event)

