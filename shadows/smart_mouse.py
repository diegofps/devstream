from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.smart_output import SmartOutputEvent
from evdev import ecodes as e
from reflex import Reflex
from shadow import Shadow

import log


#############################################################################################
# N STATE
#############################################################################################

class SmartMouseReflex_N(Reflex): # Normal Mode

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
        if event.value == 1: # +G
            self.shift_reflex("G")

    def on_H(self, event):
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

class SmartMouseReflex_H(Reflex):

    def on_A(self, event): # A
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("previous_workspace")

    def on_B(self, event): # B
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

    def on_E(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.update("SCROLL_TABS", event.value)
    
    def on_F(self, event):
        pass
        
    def on_G(self, event):
        if event.value == 1: # +G
            log.debug("Pressing G from SmartMouseReflex_H, clean is", self.clean)
            self.shift_reflex("HG")
    
    def on_H(self, event):
        if event.value == 0: # -H
            log.debug("Releasing H from SmartMouseReflex_H, clean is", self.clean)
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
    

class SmartMouseReflex_HG(Reflex): # Super H
    
    def on_A(self, event): # A
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("move_window_to_previous_workspace")

    def on_B(self, event): # B
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
    
    def on_E(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.update("SCROLL_HKEYS", event.value)
    
    def on_F(self, event):
        pass
        
    def on_G(self, event):
        if event.value == 0: # -G
            log.debug("Releasing G from SmartMouseReflex_HG, clean is", self.clean)
            self.shift_reflex("HGg", clean=False)
    
    def on_H(self, event):
        if event.value == 0: # -H
            log.debug("Releasing H from SmartMouseReflex_HG, clean is", self.clean)
            self.shift_reflex("HGh", clean=False)

    def on_I(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_Y", event.value)

    def on_J(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_X", event.value)

    def on_K(self, event):
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_RIGHT", event.value)
    
    def on_L(self, event):
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_LEFT", event.value)
    

class SmartMouseReflex_HGh(Reflex):
    
    def on_A(self, event): # A
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("minimize_window")

    def on_B(self, event): # B
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("focus_mode")
        
    def on_C(self, event):
        self.clean = False
        if event.value == 0:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("maximize_window")

    def on_H(self, event):
        if event.value == 1: # -H
            log.debug("Pressing H from SmartMouseReflex_HGh, clean is", self.clean)
            self.shift_reflex("HG", clean=False)
    
    def on_G(self, event):
        if event.value == 0: # -G
            log.debug("Releasing G from SmartMouseReflex_HGh, clean is", self.clean)
            self.shift_reflex("N", clean=False)
    
    def on_D(self, event):
        pass
    
    def on_E(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.update("SCROLL_ZOOM", event.value)
    
    def on_F(self, event):
        pass
        
    def on_I(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_Y", event.value)

    def on_J(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_X", event.value)

    def on_K(self, event):
        pass
    
    def on_L(self, event):
        pass

class SmartMouseReflex_HGg(Reflex):
    
    def on_A(self, event): # A
        pass

    def on_B(self, event): # B
        pass
        
    def on_C(self, event):
        pass

    def on_H(self, event):
        if event.value == 0: # -H
            log.debug("Releasing H from SmartMouseReflex_HGg, clean is", self.clean)
            self.shift_reflex("N", clean=False)
    
    def on_G(self, event):
        if event.value == 1: # -G
            log.debug("Pressing G from SmartMouseReflex_HGg, clean is", self.clean)
            self.shift_reflex("HG", clean=False)
    
    def on_D(self, event):
        pass
    
    def on_E(self, event):
        pass
    
    def on_F(self, event):
        pass
        
    def on_I(self, event):
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("scroll_v", event.value * 1.50)

    def on_J(self, event):
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("scroll_h", event.value * 2.00)

    def on_K(self, event):
        pass
    
    def on_L(self, event):
        pass


#############################################################################################
# G STATES
#############################################################################################

class SmartMouseReflex_G(Reflex):

    def on_deactivate(self):
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.function("select_window")
    
    def on_A(self, event): # A
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("go_to_declaration")

    def on_B(self, event): # B
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("close_window")
        
    def on_C(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("rename")

    def on_H(self, event):
        if event.value == 1: # +H
            log.debug("Pressing H from SmartMouseReflex_G, clean is", self.clean)
            self.shift_reflex("GH")
    
    def on_G(self, event):
        if event.value == 0: # -G
            log.debug("Releasing G from SmartMouseReflex_G, clean is", self.clean)

            if self.clean:
                with SmartOutputEvent(self.mind, self.source_name) as eb:
                    eb.function("navigate_back")
            
            self.shift_reflex("N")
    
    def on_D(self, event):
        pass

    def on_E(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.update("SCROLL_WINDOWS", event.value)
    
    def on_F(self, event):
        pass

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
                eb.function("redo")
    
    def on_L(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("undo")
    

class SmartMouseReflex_GH(Reflex):
    
    def on_A(self, event): # A
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("search_selection_with_duckduckgo")

    def on_B(self, event): # B
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("search_selection_with_ecosia")
        
    def on_C(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("search_selection_with_brave")
    
    def on_D(self, event):
        self.clean = False
        if event.value == 1:
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("search_selection_with_bing")
    
    def on_E(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.update("SCROLL_HKEYS", -event.value)
    
    def on_F(self, event):
        pass

    def on_G(self, event):
        if event.value == 0: # -G
            log.debug("Releasing G from SmartMouseReflex_GH, clean is", self.clean)
            self.shift_reflex("GHg", clean=False)
    
    def on_H(self, event):
        if event.value == 0: # -H
            log.debug("Releasing H from SmartMouseReflex_GH, clean is", self.clean)
            self.shift_reflex("GHh", clean=False)
    
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
    

class SmartMouseReflex_GHg(Reflex):
    
    def on_A(self, event): # A
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_PLAYPAUSE", event.value)

    def on_B(self, event): # B
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_STOPCD", event.value)
        
    def on_C(self, event):
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_MUTE", event.value)

    def on_D(self, event):
        pass
    
    def on_E(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.update("SCROLL_VOLUME", event.value)
    
    def on_F(self, event):
        pass

    def on_G(self, event):
        if event.value == 1: # +G
            log.debug("Pressing G from SmartMouseReflex_GHg, clean is", self.clean)
            self.shift_reflex("GH", clean=False)
    
    def on_H(self, event):
        if event.value == 0: # -H
            log.debug("Releasing H from SmartMouseReflex_GHg, clean is", self.clean)
            self.shift_reflex("N", clean=False)
    
    def on_I(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_Y", event.value)

    def on_J(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_X", event.value)

    def on_K(self, event):
        pass
    
    def on_L(self, event):
        pass
    

class SmartMouseReflex_GHh(Reflex):

    def on_A(self, event): # A
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_ENTER", event.value)

    def on_B(self, event): # B
        self.clean = False
        if event.value == 1: # +B
            with SmartOutputEvent(self.mind, self.source_name) as eb:
                eb.function("ctrl_c")
        
    def on_C(self, event):
        self.clean = False
        with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
            eb.update("KEY_ESC", event.value)

    def on_D(self, event):
        pass
    
    def on_E(self, event):
        self.clean = False
        with SmartOutputEvent(self.mind, self.source_name) as eb:
            eb.update("SCROLL_VKEYS", event.value)
    
    def on_F(self, event):
        pass
    
    def on_G(self, event):
        if event.value == 0: # -G
            log.debug("Releasing G from SmartMouseReflex_GHh, clean is", self.clean)
            self.shift_reflex("N", clean=False)

    def on_H(self, event):
        if event.value == 1: # +H
            log.debug("Pressing H from SmartMouseReflex_GHh, clean is", self.clean)
            self.shift_reflex("GH", clean=False)

    def on_I(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_Y", event.value)

    def on_J(self, event):
        with VirtualMouseEvent(self.mind, self.source_name) as eb:
            eb.update("REL_X", event.value)

    def on_K(self, event):
        pass
    
    def on_L(self, event):
        pass



#############################################################################################
# D STATE
#############################################################################################

class SmartMouseReflex_D(Reflex):
    
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
            log.debug(f"Releasing D from {self.name}, clean is {self.clean}")
            if self.clean:
                with VirtualKeyboardEvent(self.mind, self.source_name) as eb:
                    eb.press("KEY_LEFTMETA")
                    eb.release("KEY_LEFTMETA")
            self.shift_reflex("N")
    
    def on_E(self, event):
        # self.clean = False
        # speed = 8
        # with SmartOutputEvent(self.mind, self.source_name) as eb:
        #     eb.update("SCROLL_UNDO", -speed if event.value > 0 else speed)
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
    def on_configure(self, **kwargs):
        log.debug("Inside on_configure for SmartMouseShadow")

        self.add_reflex(SmartMouseReflex_N({**kwargs, 'autostart':True}))
        self.add_reflex(SmartMouseReflex_D(**kwargs))

        self.add_reflex(SmartMouseReflex_H(**kwargs))
        self.add_reflex(SmartMouseReflex_HG(**kwargs))
        self.add_reflex(SmartMouseReflex_HGh(**kwargs))
        self.add_reflex(SmartMouseReflex_HGg(**kwargs))

        self.add_reflex(SmartMouseReflex_G(**kwargs))
        self.add_reflex(SmartMouseReflex_GH(**kwargs))
        self.add_reflex(SmartMouseReflex_GHg(**kwargs))
        self.add_reflex(SmartMouseReflex_GHh(**kwargs))

        self.require_device(kwargs['required_devices'])
