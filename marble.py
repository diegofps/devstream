from utils import smooth, BaseConsumer
from evdev import ecodes as e
import time


TARGET_DEVICE = "Logitech USB Trackball"


class BaseMarbleConsumer(BaseConsumer):

    def __init__(self, core):
        super().__init__(core)

    def on_event(self, event):

        if event.type == e.EV_KEY:

            # big_left
            if event.code == e.BTN_LEFT:
                self.on_left_click(event)

            # small left
            elif event.code == e.BTN_SIDE:
                self.on_down_click(event)                    

            # small right
            elif event.code == e.BTN_EXTRA:
                self.on_up_click(event)

            # big right
            elif event.code == e.BTN_RIGHT:
                self.on_right_click(event)

        elif event.type == e.EV_REL:

            # Ball rotates horizontally
            if event.code == e.REL_X:
                self.on_move_rel_x(event)

            # Ball rotates vertically
            elif event.code == e.REL_Y:
                self.on_move_rel_y(event)


class Marble_N(BaseMarbleConsumer): # N

    def __init__(self, core):
        super().__init__(core)
    
    def on_left_click(self, event): # A
        self.core.out.BTN_LEFT.update(event.value)

    def on_down_click(self, event): # B
        if event.value == 1: # +B
            self.core.set_consumer(TARGET_DEVICE, "Marble_B")
    
    def on_up_click(self, event): # C
        if event.value == 1: # +C
            self.core.set_consumer(TARGET_DEVICE, "Marble_C")

    def on_right_click(self, event): # D
        if event.value == 1: # +D
            self.core.set_consumer(TARGET_DEVICE, "Marble_D")
    
    def on_move_rel_x(self, event):
        self.core.out.bt_rel_x.update(smooth(event.value))

    def on_move_rel_y(self, event):
        self.core.out.bt_rel_y.update(smooth(event.value))


class Marble_B(BaseMarbleConsumer):

    def __init__(self, core):
        super().__init__(core)
        self.clean = True
    
    def on_activate(self):
        super().on_activate()
        self.clean = True
    
    def on_deactivate(self):
        super().on_deactivate()

    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.core.out.KEY_LEFTMETA.press()

        elif event.value == 0:
            self.core.out.KEY_LEFTMETA.release()

    def on_down_click(self, event): # B
        if event.value == 0:

            if self.clean:
                self.core.out.KEY_LEFTCTRL.press()
                self.core.out.BTN_LEFT.press()

                time.sleep(0.25) # The click must happen after the IDE has created the "button"

                self.core.out.BTN_LEFT.release()
                self.core.out.KEY_LEFTCTRL.release()
            
            self.core.set_consumer(TARGET_DEVICE, "Marble_N")
    
    def on_up_click(self, event): # C
        self.clean = False
        self.core.out.BTN_SIDE.update(event.value)

    def on_right_click(self, event): # D
        self.clean = False
        self.core.out.BTN_EXTRA.update(event.value)
    
    def on_move_rel_x(self, event):
        self.clean = False
        self.core.out.bt_wheel_h.update(event.value * 20)

    def on_move_rel_y(self, event):
        self.clean = False
        self.core.out.bt_wheel_v.update(-event.value * 10)


class Marble_C(BaseMarbleConsumer):

    def __init__(self, core):
        super().__init__(core)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_T.press()
        
        else:
            self.core.out.KEY_T.release()
            self.core.out.KEY_LEFTCTRL.release()

    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 1:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_LEFTSHIFT.press()
            self.core.out.KEY_T.press()
        
        else:
            self.core.out.KEY_T.release()
            self.core.out.KEY_LEFTSHIFT.release()
            self.core.out.KEY_LEFTCTRL.release()
    
    def on_up_click(self, event): # C

        if event.value == 0: # -C

            if self.clean:
                self.core.out.BTN_RIGHT.press()
                self.core.out.BTN_RIGHT.release()
            
            self.core.out.lockable2.unlock()
            self.core.set_consumer(TARGET_DEVICE, "Marble_N")

    def on_right_click(self, event): # D
        self.clean = False
        
        if event.value == 0:
            self.core.out.KEY_LEFTALT.press()

            self.core.out.BTN_RIGHT.press()
            self.core.out.BTN_RIGHT.release()

            time.sleep(0.2)

            self.core.out.KEY_S.press()
            self.core.out.KEY_S.release()

            self.core.out.KEY_LEFTALT.release()
    
    def on_move_rel_x(self, event):
        self.clean = False
        self.core.out.lockable2.update_h(event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        self.core.out.lockable2.update_v(-event.value * 5)


class Marble_D(BaseMarbleConsumer):

    def __init__(self, core):
        super().__init__(core)
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_deactivate(self):
        self.core.out.KEY_LEFTALT.release()
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_W.press()

        else:
            self.core.out.KEY_W.release()
            self.core.out.KEY_LEFTCTRL.release()
    
    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 1:
            self.core.out.KEY_LEFTALT.press()
            self.core.out.KEY_F4.press()

        else:
            self.core.out.KEY_F4.release()
            self.core.out.KEY_LEFTALT.release()

    def on_up_click(self, event): # C
        self.clean = False

        if event.value == 1:
            self.core.out.KEY_LEFTCTRL.press()
            self.core.out.KEY_D.press()

        else:
            self.core.out.KEY_D.release()
            self.core.out.KEY_LEFTCTRL.release()
    
    def on_right_click(self, event): # D
        if event.value == 0:

            if self.clean:
                self.core.out.BTN_MIDDLE.press()
                self.core.out.BTN_MIDDLE.release()
            
            self.core.out.lockable1.unlock()

            self.core.set_consumer(TARGET_DEVICE, "Marble_N")
    
    def on_move_rel_x(self, event):
        self.clean = False
        self.core.out.lockable1.update_h(event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        self.core.out.lockable1.update_v(-event.value * 5)


def on_init(core):

    core.consumers["Marble_N"] = Marble_N(core)
    # core.consumers["MarbleA"] = MarbleA(core)
    core.consumers["Marble_B"] = Marble_B(core)
    core.consumers["Marble_C"] = Marble_C(core)
    core.consumers["Marble_D"] = Marble_D(core)

    core.listeners[TARGET_DEVICE] = core.consumers["Marble_N"]
