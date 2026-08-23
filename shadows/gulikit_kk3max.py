from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.smart_output import SmartOutputEvent
from evdev import ecodes as e
from reflex import Reflex
from shadow import Shadow

import log

SOURCE_JOYPAD    = "GULIKIT KK3 MAX"
REQUIRED_DEVICES = [
    "ZhiXu GuliKit Controller A",
    "Microsoft X-Box 360 pad"
]


class BaseJoypadNode(Reflex):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean = True
    
    def on_event(self, device_name, event):
        # self.debug_event(device_name, event)

        if event.type == e.EV_KEY:

            if event.code == e.BTN_NORTH:
                self.on_btn_left(event)

            elif event.code == e.BTN_SOUTH:
                self.on_btn_bottom(event)

            elif event.code == e.BTN_EAST:
                self.on_btn_right(event)

            elif event.code == e.BTN_WEST:
                self.on_btn_top(event)

            elif event.code == e.BTN_START:
                self.on_start(event)

            elif event.code == e.BTN_SELECT:
                self.on_select(event)

            elif event.code == e.KEY_HOMEPAGE:
                self.on_home(event)

            elif event.code == e.BTN_TR:
                self.on_r1(event)

            elif event.code == e.BTN_TL:
                self.on_l1(event)

            elif event.code == e.BTN_TR2:
                self.on_r2(event)

            elif event.code == e.BTN_TL2:
                self.on_l2(event)

            elif event.code == e.BTN_THUMBL:
                self.on_thumb_left(event)
            
            elif event.code == e.BTN_THUMBR:
                self.on_thumb_right(event)
            
            else:
                self.debug_event(device_name, event)

        elif event.type == e.EV_ABS:

            if event.code == e.ABS_GAS:
                self.on_r2_fuzzy(event)

            elif event.code == e.ABS_BRAKE:
                self.on_l2_fuzzy(event)

            elif event.code == e.ABS_HAT0X:
                self.on_hat_x(event)

            elif event.code == e.ABS_HAT0Y:
                self.on_hat_y(event)

            elif event.code == e.ABS_X:
                self.on_abs_right_x(event)

            elif event.code == e.ABS_Y:
                self.on_abs_right_y(event)

            elif event.code == e.ABS_Z:
                self.on_abs_left_x(event)

            elif event.code == e.ABS_RZ:
                self.on_abs_left_y(event)

            else:
                self.debug_event(device_name, event)
        
        else:
            self.debug_event(device_name, event)

    def on_activate(self, clean=True):
        log.debug(f"{self.name} is activating, clean={clean}")
        self.clean = clean

    def on_deactivate(self):
        log.debug(f"{self.name} is deactivating")


class Joypad_N(BaseJoypadNode): # Normal

    def on_start(self, event):
        pass
    
    def on_select(self, event):
        pass
    
    def on_home(self, event):
        with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
            eb.update("KEY_H", event.value)
    

    def on_l1(self, event):
        pass
    
    def on_r1(self, event):
        pass

    def on_l2(self, event):
        with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
            eb.update("KEY_Z", event.value)
    
    def on_r2(self, event):
        with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
            eb.update("KEY_X", event.value)
    
    def on_l2_fuzzy(self, event):
        pass
    
    def on_r2_fuzzy(self, event):
        pass
    

    def on_hat_x(self, event):
        if event.value == -1:
            with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
                eb.press("KEY_COMMA")

        elif event.value == 1:
            with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
                eb.press("KEY_SLASH")
            
        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
                eb.release("KEY_COMMA")
                eb.release("KEY_SLASH")
    
    def on_hat_y(self, event):
        if event.value == 0:
            with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
                eb.release("KEY_DOT")
            
        else:
            with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
                eb.press("KEY_DOT")


    def on_thumb_left(self, event):
        pass
    
    def on_thumb_right(self, event):
        pass
    

    def on_abs_left_x(self, event):
        pass
    
    def on_abs_left_y(self, event):
        pass
    

    def on_abs_right_x(self, event):
        pass
    
    def on_abs_right_y(self, event):
        pass
    

    def on_btn_top(self, event):
        pass
    
    def on_btn_bottom(self, event):
        with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
            eb.update("KEY_SPACE", event.value)
    
    def on_btn_left(self, event):
        with VirtualKeyboardEvent(self.mind, SOURCE_JOYPAD) as eb:
            eb.update("KEY_B", event.value)
    
    def on_btn_right(self, event):
        pass


class GulikitKK3Max(Shadow):
    def on_configure(self):
        self.add_reflex(Joypad_N(required_devices=REQUIRED_DEVICES, source_name=SOURCE_JOYPAD, autostart=True))
        self.require_device(REQUIRED_DEVICES)

