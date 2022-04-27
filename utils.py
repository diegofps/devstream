from evdev import InputDevice, list_devices

def grab_device(name):
    devices = [InputDevice(path) for path in list_devices()]
    for d in devices:
        if d.name == name:
            d.grab()
            return d
    return None

def smooth(v):
    return int(v * 1.5)
