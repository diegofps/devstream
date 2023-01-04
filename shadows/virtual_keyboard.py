from evdev import UInput, ecodes as e

from .virtual_device import VirtualDevice, VirtualDeviceEvent


TOPIC_VIRTUALKEYBOARD_EVENT = "VirtualKeyboard"


class VirtualKeyboardEvent(VirtualDeviceEvent):
    def __init__(self, mind, source):
        super().__init__(mind, TOPIC_VIRTUALKEYBOARD_EVENT, source)


class VirtualKeyboard(VirtualDevice):

    def __init__(self, shadow):
        super().__init__(shadow, "devstream_keyboard")
        
        self.init_keys()
        self.add_listener(TOPIC_VIRTUALKEYBOARD_EVENT, self.on_event)

    def get_capabilities(self):
        return {
            e.EV_KEY : [
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
                e.KEY_RESERVED, 
                # e.KEY_BRIGHTNESSDOWN, e.KEY_BRIGHTNESSUP, e.KEY_DISPLAYTOGGLE,

                # e.KEY_KP0, e.KEY_KP1, e.KEY_KP2, e.KEY_KP3, e.KEY_KP4, e.KEY_KP5, e.KEY_KP6, e.KEY_KP7, e.KEY_KP8, e.KEY_KP9,
                # e.KEY_KPMINUS, e.KEY_KPPLUS, e.KEY_KPENTER, e.KEY_KPDOT, e.KEY_KPSLASH, e.KEY_KPASTERISK, e.KEY_NUMLOCK,

            ],

            e.EV_ABS: [
                
            ],

            e.EV_REL : [
                
            ],

            e.EV_MSC : [
                
            ]
        }

    def init_keys(self):

        self.add_keys([
            "LEFTALT", "LEFTCTRL", "LEFTMETA", "LEFTSHIFT", "RIGHTALT", "RIGHTCTRL", "RIGHTMETA", "RIGHTSHIFT", 
            "PLAYPAUSE", "NEXTSONG", "PREVIOUSSONG", "STOPCD", "MUTE", "VOLUMEUP", "VOLUMEDOWN", 

            "TAB", "PAGEDOWN", "PAGEUP", "EQUAL", "MINUS", "ESC",
            "PRINT", "HOME", "END", "COMMA", "SLASH", "DOT", 
            "APOSTROPHE", "BACKSLASH", "LEFTBRACE", "RIGHTBRACE", 
            "SEMICOLON", "SPACE", "CAPSLOCK", "GRAVE", "SCROLLLOCK", 
            "SYSRQ", "PAUSE", "DELETE", "INSERT", "RO", "BACKSPACE", 
            "LEFT", "RIGHT", "UP", "DOWN", "ENTER", "102ND", 

            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",

            # "KP0", "KP1", "KP2", "KP3", "KP4", "KP5", "KP6", "KP7", "KP8", "KP9",
            # "KPMINUS", "KPPLUS", "KPENTER", "KPDOT", "KPSLASH", "KPASTERISK", "NUMLOCK",
        ])

def on_load(shadow):
    VirtualKeyboard(shadow)
