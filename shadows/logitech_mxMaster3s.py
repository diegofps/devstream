from shadows.virtual_keyboard import VirtualKeyboardEvent
from shadows.virtual_mouse import VirtualMouseEvent
from shadows.smart_output import SmartOutputEvent
from shadows.smart_mouse import SmartMouseShadow
from evdev import ecodes as e
from reflex import Reflex
from shadow import Shadow


REQUIRED_DEVICES = [
    "Logitech MX Master 3S",
    "LogiOps Virtual Input"
]

SOURCE_LOGITECH_MXMASTER3S = "Logi MX Master 3S"


class MXMaster3S_LogidMonitor(Reflex):

    def on_configure(self):
        super().on_configure()
        self.require_daemon()
    
    def run(self, daemon):
        self.log.debug(f"Starting LogidMonitor daemon thread")

        from subprocess import Popen, PIPE
        import shlex
        import time
        import os

        while not daemon.done:
            try:
                cmd = shlex.split("journalctl --lines 1 -u logid")

                with Popen(cmd, stdout=PIPE) as proc:
                    lines = proc.stdout.readlines()

                if lines and lines[0].decode('utf-8').endswith('after 5 tries. Treating as failure.\n'):
                    self.log.info('Detected logid is in a failure state, restarting the service')
                    os.system('service logid restart')
                
            except Exception as e:
                self.log.error(f"Failed to monitor logid service: {e}")
            
            time.sleep(3)
        
        self.log.debug(f"Ending LogidMonitor daemon thread")


def mxMaster3SEventWrapper(reflex, device_name, event, target):
    # log.debug(f"Event received from {device_name}: {event}")

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

        elif event.code == e.BTN_FORWARD:
            target.on_D(event)
            
        elif event.code == e.KEY_A:
            reflex.log.debug("KEY_A event")
            
        elif event.code == e.KEY_B:
            # log.debug("KEY_B event")
            target.on_B(event)

    elif event.type == e.EV_REL:

        if event.code == e.REL_X:
            target.on_J(event)

        elif event.code == e.REL_Y:
            target.on_I(event)

        elif event.code == e.REL_WHEEL_HI_RES:
            target.on_E(event)

        elif event.code == e.REL_HWHEEL_HI_RES:
            event.value = -event.value
            target.on_F(event)


class LogitechMXMaster3S(SmartMouseShadow):
    def on_configure(self):
        self.log.debug("Configuring MXMaster3S")
        super().on_configure(required_devices=REQUIRED_DEVICES)
        self.configure_SmartMouse(event_wrapper=mxMaster3SEventWrapper)
        self.add_reflex(MXMaster3S_LogidMonitor, keepalive=True)

