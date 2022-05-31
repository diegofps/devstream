#!/usr/bin/env python3

import inotify.adapters

def _main():
    i = inotify.adapters.Inotify()

    i.add_watch('/media/diego')

    for event in i.event_gen(yield_nones=False):
        (first, type_names, path, filename) = event

        print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={} FIRST={}".format(
              path, filename, type_names, first))

if __name__ == '__main__':
    _main()


# NODE: BaseDevice
# NAME: Corsair Keyboard
# PATH: /dev/input/event21
# TYPE: EV_KEY
# CODE: KEY_ENTER
# EVENT_VALUE: 1
# RAW: ...


