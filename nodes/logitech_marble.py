from utils import smooth, BaseNode, debug, info, warn, error
from nodes.device_writer import OutputEvent
from evdev import ecodes as e
import time


REQUIRED_DEVICES = [
    "Logitech USB Trackball"
]

TOPIC_DEVICE_MARBLE = "DeviceReader:Logitech USB Trackball"
TOPIC_MARBLE_STATE = "Marble:State"


class BaseMarbleNode(BaseNode):

    def __init__(self, core, name):
        super().__init__(core, name)
        core.register_listener(TOPIC_MARBLE_STATE, self.on_state_changed)
        self.active = False

    def on_state_changed(self, topic_name, package):
        # debug(self.name, "received state_changed event", topic_name, package)
        if package.startswith(self.name):
            if not self.active:
                self.active = True
                self.on_activate()
            
            self.core.register_listener(TOPIC_DEVICE_MARBLE, self.on_event)

        else:
            if self.active:
                self.active = False
                self.on_deactivate()
            
            self.core.unregister_listener(TOPIC_DEVICE_MARBLE, self.on_event)

    def on_event(self, topic_name, event):
        # debug("Marble is receiving a mouse event", topic_name, event)

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
    
    def on_activate(self):
        pass

    def on_deactivate(self):
        pass


class Marble_N(BaseMarbleNode): # N

    def __init__(self, core):
        super().__init__(core, "Marble_N")
    
    def on_left_click(self, event): # A
        # self.core.out.BTN_LEFT.update(event.value)
        # self.core.emit(TOPIC_DEVICEWRITER_EVENT, EventType.UPDATE, "BTN_LEFT", event.value)
        #self.emitUpdate("BTN_LEFT", event.value)
        with OutputEvent(self.core) as eb:
            eb.update("BTN_LEFT", event.value)
        
    def on_down_click(self, event): # B
        if event.value == 1: # +B
            self.core.emit(TOPIC_MARBLE_STATE, "Marble_B")
    
    def on_up_click(self, event): # C
        if event.value == 1: # +C
            self.core.emit(TOPIC_MARBLE_STATE, "Marble_C")

    def on_right_click(self, event): # D
        if event.value == 1: # +D
            self.core.emit(TOPIC_MARBLE_STATE, "Marble_D")
    
    def on_move_rel_x(self, event):
        # self.core.out.REL_X.update(smooth(event.value))
        # self.core.emit(TOPIC_DEVICEWRITER_EVENT, EventType.UPDATE, "REL_X", smooth(event.value))
        # self.emitUpdate("REL_X", smooth(event.value))
        with OutputEvent(self.core) as eb:
            eb.update("REL_X", smooth(event.value))
        
    def on_move_rel_y(self, event):
        # self.core.out.REL_Y.update(smooth(event.value))
        # self.core.emit(TOPIC_DEVICEWRITER_EVENT, EventType.UPDATE, "REL_Y", smooth(event.value))
        # self.emitUpdate("REL_Y", smooth(event.value))
        with OutputEvent(self.core) as eb:
            eb.update("REL_Y", smooth(event.value))


class Marble_B(BaseMarbleNode):

    def __init__(self, core):
        super().__init__(core, "Marble_B")
        self.clean = True
    
    def on_activate(self):
        super().on_activate()
        self.clean = True
    
    def on_deactivate(self):
        super().on_deactivate()

    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            # self.core.out.KEY_LEFTMETA.press()
            # self.emitPress("KEY_LEFTMETA")

            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTMETA")

        elif event.value == 0:
            # self.core.out.KEY_LEFTMETA.release()
            # self.emitRelease("KEY_LEFTMETA")
            with OutputEvent(self.core) as eb:
                eb.release("KEY_LEFTMETA")

    def on_down_click(self, event): # B
        if event.value == 0:

            if self.clean:
                # self.emitFunction("control_left_click")

                with OutputEvent(self.core) as eb:
                    eb.press("KEY_LEFTCTRL")
                    eb.press("BTN_LEFT")
                    eb.sleep(0.25)
                    eb.release("BTN_LEFT")
                    eb.release("KEY_LEFTCTRL")
                
                # self.core.out.KEY_LEFTCTRL.press()
                # self.core.out.BTN_LEFT.press()

                # time.sleep(0.25) # The click must happen after the IDE has created the "button"

                # self.core.out.BTN_LEFT.release()
                # self.core.out.KEY_LEFTCTRL.release()
            
            self.core.emit(TOPIC_MARBLE_STATE, "Marble_N")
    
    def on_up_click(self, event): # C
        self.clean = False
        # self.core.out.BTN_SIDE.update(event.value)
        # self.emitUpdate("BTN_SIDE", event.value)
        with OutputEvent(self.core) as eb:
            eb.update("BTN_SIDE", event.value)

    def on_right_click(self, event): # D
        self.clean = False
        # self.core.out.BTN_EXTRA.update(event.value)
        # self.emitUpdate("BTN_EXTRA", event.value)

        with OutputEvent(self.core) as eb:
            eb.update("BTN_EXTRA", event.value)
    
    def on_move_rel_x(self, event):
        self.clean = False
        # self.core.out.bt_wheel_h.update(event.value * 20)
        # self.emitUpdate("WHEEL_H", event.value * 20)
        with OutputEvent(self.core) as eb:
            eb.update("WHEEL_H", event.value * 20)

    def on_move_rel_y(self, event):
        self.clean = False
        # self.core.out.bt_wheel_v.update(-event.value * 10)
        # self.emitUpdate("WHEEL_V", event.value * 10)
        with OutputEvent(self.core) as eb:
            eb.update("WHEEL_V", -event.value * 10)



class Marble_C(BaseMarbleNode):

    def __init__(self, core):
        super().__init__(core, "Marble_C")
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False
        
        if event.value == 0:
            # self.core.out.KEY_LEFTALT.press()

            # self.core.out.BTN_RIGHT.press()
            # self.core.out.BTN_RIGHT.release()

            # time.sleep(0.2)

            # self.core.out.KEY_LEFTALT.release()

            # self.core.out.KEY_S.press()
            # self.core.out.KEY_S.release()
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTALT")
                eb.press("BTN_RIGHT")
                eb.release("BTN_RIGHT")
                eb.sleep(0.2)
                eb.release("KEY_LEFTALT")
                eb.press("KEY_S")
                eb.release("KEY_S")


    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 1:
            # self.core.out.KEY_LEFTCTRL.press()
            # self.core.out.KEY_LEFTSHIFT.press()
            # self.core.out.KEY_T.press()
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_LEFTSHIFT")
                eb.press("KEY_T")

        else:
            # self.core.out.KEY_T.release()
            # self.core.out.KEY_LEFTSHIFT.release()
            # self.core.out.KEY_LEFTCTRL.release()
            with OutputEvent(self.core) as eb:
                eb.release("KEY_T")
                eb.release("KEY_LEFTSHIFT")
                eb.release("KEY_LEFTCTRL")
    
    def on_up_click(self, event): # C

        if event.value == 0: # -C

            with OutputEvent(self.core) as eb:
                if self.clean:
                    # self.core.out.BTN_RIGHT.press()
                    # self.core.out.BTN_RIGHT.release()
                    eb.press("BTN_RIGHT")
                    eb.release("BTN_RIGHT")
            
                #self.core.out.lockable2.unlock()
                eb.unlock("DUAL_UNDO_VOLUME")
            
            self.core.emit(TOPIC_MARBLE_STATE, "Marble_N")

    def on_right_click(self, event): # D
        self.clean = False

        if event.value == 1:
            # self.core.out.KEY_LEFTCTRL.press()
            # self.core.out.KEY_T.press()
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_T")
        
        else:
            # self.core.out.KEY_T.release()
            # self.core.out.KEY_LEFTCTRL.release()
            with OutputEvent(self.core) as eb:
                eb.release("KEY_T")
                eb.release("KEY_LEFTCTRL")
    
    def on_move_rel_x(self, event):
        self.clean = False
        # self.core.out.lockable2.update_h(event.value * 5)
        with OutputEvent(self.core) as eb:
            eb.update_h("DUAL_UNDO_VOLUME", event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        # self.core.out.lockable2.update_v(-event.value * 5)
        with OutputEvent(self.core) as eb:
            eb.update_v("DUAL_UNDO_VOLUME", -event.value * 5)


class Marble_D(BaseMarbleNode):

    def __init__(self, core):
        super().__init__(core, "Marble_D")
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_deactivate(self):
        # self.core.out.KEY_LEFTALT.release()
        with OutputEvent(self.core) as eb:
            eb.release("KEY_LEFTALT")
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            # self.core.out.KEY_LEFTCTRL.press()
            # self.core.out.KEY_W.press()
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_W")

        else:
            # self.core.out.KEY_W.release()
            # self.core.out.KEY_LEFTCTRL.release()
            with OutputEvent(self.core) as eb:
                eb.release("KEY_W")
                eb.release("KEY_LEFTCTRL")
    
    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 1:
            # self.core.out.KEY_LEFTALT.press()
            # self.core.out.KEY_F4.press()
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTALT")
                eb.press("KEY_F4")

        else:
            # self.core.out.KEY_F4.release()
            # self.core.out.KEY_LEFTALT.release()
            with OutputEvent(self.core) as eb:
                eb.release("KEY_F4")
                eb.release("KEY_LEFTALT")

    def on_up_click(self, event): # C
        self.clean = False

        if event.value == 1:
            # self.core.out.KEY_LEFTCTRL.press()
            # self.core.out.KEY_D.press()
            with OutputEvent(self.core) as eb:
                eb.press("KEY_LEFTCTRL")
                eb.press("KEY_D")

        else:
            # self.core.out.KEY_D.release()
            # self.core.out.KEY_LEFTCTRL.release()
            with OutputEvent(self.core) as eb:
                eb.release("KEY_D")
                eb.release("KEY_LEFTCTRL")
    
    def on_right_click(self, event): # D
        if event.value == 0:

            with OutputEvent(self.core) as eb:
                if self.clean:
                    # self.core.out.BTN_MIDDLE.press()
                    # self.core.out.BTN_MIDDLE.release()
                    eb.press("BTN_MIDDLE")
                    eb.release("BTN_MIDDLE")
            
                # self.core.out.lockable1.unlock()
                eb.unlock("DUAL_WINDOWS_TABS")

            self.core.emit(TOPIC_MARBLE_STATE, "Marble_N")
    
    def on_move_rel_x(self, event):
        self.clean = False
        # self.core.out.lockable1.update_h(event.value * 5)
        with OutputEvent(self.core) as eb:
            eb.update_h("DUAL_WINDOWS_TABS", event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        # self.core.out.lockable1.update_v(-event.value * 5)
        with OutputEvent(self.core) as eb:
            eb.update_v("DUAL_WINDOWS_TABS", -event.value * 5)


def on_init(core):

    core.add_node("Marble_N", Marble_N(core))
    # core.add_consumer("MarbleA", MarbleA(core))
    core.add_node("Marble_B", Marble_B(core))
    core.add_node("Marble_C", Marble_C(core))
    core.add_node("Marble_D", Marble_D(core))

    core.require_device(REQUIRED_DEVICES)
    core.emit(TOPIC_MARBLE_STATE, "Marble_N")

