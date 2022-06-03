#!/usr/bin/env python3

from evdev import InputDevice, AbsInfo, UInput, list_devices, ecodes as e
import evdev
import sys

print("row;fd;version;ff_effects_count;uniq;phys;path;name;info.version;info.product;info.vendor;info.bustype")

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for i, d in enumerate([evdev.InputDevice(path) for path in evdev.list_devices()]):
    import pdb
    pdb.set_trace()

    print("%d;%d;%d;%d; %s;%s;%s;%s; %d;%d;%d;%d" % (i, d.fd, d.version, d.ff_effects_count, d.uniq, d.phys, d.path, d.name, d.info.version, d.info.product, d.info.vendor, d.info.bustype))

sys.exit(0)

