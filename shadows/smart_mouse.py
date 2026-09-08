from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.smart_output import SmartOutputEvent
from keys import AdversarialDelayedKey
from evdev import ecodes as e
from reflex import Reflex
from shadow import Shadow




#############################################################################################
# BASE STATE CLASS
#############################################################################################

class SmartMouseReflex(Reflex):

    def __init__(self, 
                IJ_size=100, IJ_axis_lockable=False, IJ_single_shot=True, 
                E_size=250, E_axis_lockable=False, E_single_shot=False, 
                F_size=250, F_axis_lockable=False, F_single_shot=False, 
                select_window_on_deactivate=False, **kwargs):
        
        super().__init__(**kwargs)

        self.select_window_on_deactivate = select_window_on_deactivate
        self.scroll_IJ = AdversarialDelayedKey("scroll_IJ", self.on_event_J, self.on_event_I, IJ_size, self.log, IJ_axis_lockable, IJ_single_shot)
        self.scroll_E = AdversarialDelayedKey("scroll_E", self.on_event_E, self.on_event_E, E_size, self.log, E_axis_lockable, E_single_shot)
        self.scroll_F = AdversarialDelayedKey("scroll_F", self.on_event_F, self.on_event_F, F_size, self.log, F_axis_lockable, F_single_shot)

    def on_deactivate(self):
        super().on_deactivate()

        self.scroll_IJ.clear()
        self.scroll_E.clear()
        self.scroll_F.clear()

        if self.select_window_on_deactivate:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("select_window")

    def on_E(self, event):
        self.scroll_E.update_v(event.value)
    
    def on_F(self, event):
        self.scroll_F.update_h(event.value)

    def on_I(self, event):
        self.scroll_IJ.update_v(event.value)

    def on_J(self, event):
        self.scroll_IJ.update_h(event.value)
    
    def on_event_I(self, value):
        pass

    def on_event_J(self, value):
        pass

    def on_event_E(self, value):
        pass

    def on_event_F(self, value):
        pass



    
#############################################################################################
# N STATE
#############################################################################################

class SmartMouseReflex_N(SmartMouseReflex): # Normal Mode

    def on_A(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("BTN_LEFT", event.value)

    def on_B(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("BTN_MIDDLE", event.value)
        
    def on_C(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("BTN_RIGHT", event.value)

    def on_D(self, event):
        if event.value == 1: # +F
            self.shift_reflex("D")

    def on_E(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("WHEEL_V", event.value)
    
    def on_F(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("WHEEL_H", event.value)
    
    def on_G(self, event):
        self.log.debug(f"Switching to G, event={event}")
        if event.value == 1: # +G
            self.shift_reflex("G")

    def on_H(self, event):
        self.log.debug(f"Switching to H, event={event}")
        if event.value == 1: # +H
            self.shift_reflex("H")
    
    def on_I(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_Y", event.value)

    def on_J(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_X", event.value)

    def on_K(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("WHEEL_H", +120)
    
    def on_L(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("WHEEL_H", -120)
    

#############################################################################################
# H STATES
#############################################################################################

class SmartMouseReflex_H(SmartMouseReflex):

    def on_A(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("previous_workspace")

    def on_B(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("close_tab")
            
    def on_C(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("next_workspace")

    def on_D(self, event):
        pass

    def on_event_E(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("next_tab" if value > 0 else "previous_tab")

    def on_event_F(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("brightness_up" if value > 0 else "brightness_down")
    
    def on_G(self, event):
        if event.value == 1: # +G
            self.log.debug("Pressing G from SmartMouseReflex_H, clean is", self.clean)
            self.shift_reflex("HG")
    
    def on_H(self, event):
        if event.value == 0: # -H
            self.log.debug("Releasing H from SmartMouseReflex_H, clean is", self.clean)
            if self.clean:
                with SmartOutputEvent(self.mind, self.source_name) as eb:
                    eb.function("navigate_forward")
            self.shift_reflex("N")

    def on_I(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_Y", event.value)

    def on_J(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_X", event.value)

    def on_K(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("zoom_in")
    
    def on_L(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("zoom_out")


class SmartMouseReflex_HG(SmartMouseReflex):
    
    def __init__(self, **kwargs):
        super().__init__(E_single_shot=True, F_single_shot=True, **kwargs)
    
    def on_A(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("move_window_to_previous_workspace")

    def on_B(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("reopen_tab")
        
    def on_C(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("move_window_to_next_workspace")

    def on_D(self, event):
        pass

    def on_event_E(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("maximize_window" if value > 0 else "minimize_window")

    def on_event_F(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("place_window_right" if value > 0 else "place_window_left")
    
    def on_G(self, event):
        if event.value == 0: # -G
            self.log.debug("Releasing G from SmartMouseReflex_HG, clean is", self.clean)
            self.shift_reflex("H", clean=False)
    
    def on_H(self, event):
        if event.value == 0: # -H
            self.log.debug("Releasing H from SmartMouseReflex_HG, clean is", self.clean)
            self.shift_reflex("HGh", clean=False)

    def on_I(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_Y", event.value)

    def on_J(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_X", event.value)

    def on_K(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("place_window_right", event.value)
    
    def on_L(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("place_window_left", event.value)
    

class SmartMouseReflex_HGh(SmartMouseReflex):

    def __init__(self, **kwargs):
        super().__init__(select_window_on_deactivate=True, **kwargs)
    
    def on_A(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("reboot")

    def on_B(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("lock")
        
    def on_C(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("poweroff")

    def on_D(self, event):
        pass
    
    def on_event_E(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("zoom_in" if value > 0 else "zoom_out")

    def on_event_F(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("next_window" if value > 0 else "previous_window")

    def on_G(self, event):
        if event.value == 0: # -G
            self.log.debug("Releasing G from SmartMouseReflex_HGh, clean is", self.clean)
            self.shift_reflex("N", clean=False)
    
    def on_H(self, event):
        if event.value == 1: # -H
            self.log.debug("Pressing H from SmartMouseReflex_HGh, clean is", self.clean)
            self.shift_reflex("HG", clean=False)
    
    def on_I(self, event):
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("scroll_v", event.value)

    def on_J(self, event):
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("scroll_h", event.value)

    def on_K(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("next_window", event.value)
    
    def on_L(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("previous_window", event.value)



#############################################################################################
# G STATES
#############################################################################################

class SmartMouseReflex_G(SmartMouseReflex):

    def __init__(self, **kwargs):
        super().__init__(select_window_on_deactivate=True, IJ_single_shot=True, **kwargs)
    
    def on_A(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("previous_window")

    def on_B(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("close_window")
        
    def on_C(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("next_window")
    
    def on_D(self, event):
        pass
    
    def on_event_E(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("next_window" if value > 0 else "previous_window")

    def on_event_F(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("undo" if value > 0 else "redo")

    def on_G(self, event):
        if event.value == 0: # -G
            self.log.debug("Releasing G from SmartMouseReflex_G, clean is", self.clean)
            if self.clean:
                with SmartOutputEvent(self.mind, self.source_name) as eb:
                    eb.function("navigate_back")
            self.shift_reflex("N")
    
    def on_H(self, event):
        if event.value == 1: # +H
            self.log.debug("Pressing H from SmartMouseReflex_G, clean is", self.clean)
            self.shift_reflex("GH")
    
    def on_event_I(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("search_selection_with_bing" if value > 0 else "search_selection_with_duckduckgo")

    def on_event_J(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("search_selection_with_brave" if value > 0 else "search_selection_with_ecosia")

    def on_K(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("redo")
    
    def on_L(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("undo")


class SmartMouseReflex_GH(SmartMouseReflex):
    
    def on_A(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("go_to_declaration")

    def on_B(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("focus_mode")
        
    def on_C(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("rename")

    def on_D(self, event):
        pass

    def on_E(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("WHEEL_V", event.value * 10)
    
    def on_F(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("WHEEL_H", event.value * 10)
    
    def on_G(self, event):
        if event.value == 0: # -G
            self.log.debug("Releasing G from SmartMouseReflex_GH, clean is", self.clean)
            self.shift_reflex("GHg", clean=False)
    
    def on_H(self, event):
        if event.value == 0: # -H
            self.log.debug("Releasing H from SmartMouseReflex_GH, clean is", self.clean)
            self.shift_reflex("G", clean=False)
    
    def on_I(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_Y", event.value)

    def on_J(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_X", event.value)

    def on_K(self, event):
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_NEXTSONG", event.value)
    
    def on_L(self, event):
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_PREVIOUSSONG", event.value)
    

class SmartMouseReflex_GHg(SmartMouseReflex):
    
    def on_A(self, event):
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_PLAYPAUSE", event.value)

    def on_B(self, event):
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_STOPCD", event.value)
        
    def on_C(self, event):
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_MUTE", event.value)

    def on_D(self, event):
        pass

    def on_event_E(self, value):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("volume_up" if value > 0 else "volume_down")

    def on_event_F(self, value):
        pass

    def on_G(self, event):
        if event.value == 1: # +G
            self.log.debug("Pressing G from SmartMouseReflex_GHg, clean is", self.clean)
            self.shift_reflex("GH", clean=False)
    
    def on_H(self, event):
        if event.value == 0: # -H
            self.log.debug("Releasing H from SmartMouseReflex_GHg, clean is", self.clean)
            self.shift_reflex("N", clean=False)

    def on_I(self, event):
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("scroll_v", event.value)

    def on_J(self, event):
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("scroll_h", event.value)

    def on_K(self, event):
        pass
    
    def on_L(self, event):
        pass
        


#############################################################################################
# D STATE
#############################################################################################

class SmartMouseReflex_D(SmartMouseReflex):
    
    def on_A(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("reboot")

    def on_B(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("lock")
        
    def on_C(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("poweroff")

    def on_D(self, event):
        if event.value == 0:
            self.log.debug(f"Releasing D from {self.name}, clean is {self.clean}")
            if self.clean:
                with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")
            self.shift_reflex("N")
    
    def on_E(self, event):
        pass
    
    def on_F(self, event):
        pass

    def on_G(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("ctrl_d")
    
    def on_H(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("ctrl_c")
    
    def on_I(self, event):
        pass

    def on_J(self, event): # J
        pass

    def on_K(self, event):
        pass
    
    def on_L(self, event):
        pass




#############################################################################################
# Shadow Declaration
#############################################################################################

class SmartMouseShadow(Shadow):
        
    def configure_SmartMouse(self, **kwargs):
        self.log.debug(f"Inside configure for SmartMouseShadow, kwargs={kwargs}")

        self.add_reflex(SmartMouseReflex_N, autostart=True, **kwargs)
        self.add_reflex(SmartMouseReflex_D, **kwargs)

        self.add_reflex(SmartMouseReflex_H, **kwargs)
        self.add_reflex(SmartMouseReflex_HG, **kwargs)
        self.add_reflex(SmartMouseReflex_HGh, **kwargs)

        self.add_reflex(SmartMouseReflex_G, **kwargs)
        self.add_reflex(SmartMouseReflex_GH, **kwargs)
        self.add_reflex(SmartMouseReflex_GHg, **kwargs)
