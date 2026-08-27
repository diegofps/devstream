from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.smart_output import SmartOutputEvent
from shadows.smart_mouse import SmartMouseShadow
from evdev import ecodes as e

REQUIRED_DEVICES = [
    "Logitech MX Anywhere 2S",
    "MX Anywhere 2S Mouse",
]

SOURCE_LOGITECH_MX2S = "Logitech MX2S"

def mxAnywhere2SEventWrapper(reflex, device_name, event, target):
    # reflex.log.debug("Inside mxAnywhere2SEventWrapper for dev_name=" + device_name)

    if event.type == e.EV_KEY:

        if event.code == e.BTN_LEFT:
            target.on_A(event)

        elif event.code == e.BTN_MIDDLE:
            target.on_B(event)

        elif event.code == e.BTN_RIGHT:
            target.on_C(event)

        elif event.code == e.BTN_SIDE:
            target.on_G(event)

        elif event.code == e.BTN_EXTRA:
            target.on_H(event)

    elif event.type == e.EV_REL:

        if event.code == e.REL_X:
            target.on_J(event)

        elif event.code == e.REL_Y:
            target.on_I(event)

        elif event.code == e.REL_WHEEL_HI_RES:
            target.on_E(event)

        elif event.code == e.REL_HWHEEL_HI_RES:

            if event.value < 0:
                event.value = 1
                target.on_K(event)

                event.value = 0
                target.on_K(event)
            
            else:
                event.value = 1
                target.on_L(event)

                event.value = 0
                target.on_L(event)


class LogitechMXAnywhere2S(SmartMouseShadow):
    def on_configure(self):
        super().on_configure(required_devices=REQUIRED_DEVICES, source_name=SOURCE_LOGITECH_MX2S)
        self.configure_SmartMouse(event_wrapper=mxAnywhere2SEventWrapper)

