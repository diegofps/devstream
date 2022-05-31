#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from nodes.device_writer import DeviceWriter
from nodes.device_reader import DeviceReader
from evdev import list_devices, InputDevice
from nodes.watch_windows import WatchWindows
from utils import warn, error, info, debug
from utils import init_logger


import importlib
import evdev
import time
import sys
import os

os.nice(-20)


if len(sys.argv) == 1:
    init_logger("DEBUG")
else:
    init_logger(sys.argv[1])


class Core:

    def __init__(self):

        self.listeners = {}
        self.nodes = {}
        
        self.devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self.device_names = set([dev.name for dev in self.devices])
        self.required_devices = set()

    def require_device(self, device_name):
        self.required_devices.add(device_name)
    
    def load_node_module(self, name):
        mod = importlib.import_module(name)
        mod.on_init(self)

    def add_node(self, consumer_name, consumer):
        self.nodes[consumer_name] = consumer
    
    def register_listener(self, topic_name, node):
        
        if isinstance(topic_name, list):
            for name in topic_name:
                self.register_listener(name, topic_name)
        
        elif not topic_name in self.listeners:
            self.listeners[topic_name] = [node]
        
        else:
            self.listeners[topic_name].append(node)

    def unregister_listener(self, topic_name, node):
    
        if isinstance(topic_name, list):
            for name in topic_name:
                self.unregister_listener(name, topic_name)

        elif topic_name in self.listeners:
            self.listeners[topic_name].remove(node)
    

    def start(self):

        with ThreadPoolExecutor(max_workers=1) as executor:
            self.executor = executor

            # Start output virtual device node
            self.add_node("DeviceWriter", DeviceWriter(self))

            # Start window manager monitor
            self.add_node("WatchWindows", WatchWindows(self))

            # Start disk monitor
            # TODO

            # Start device monitor
            # TODO

            # Start consumers
            self.load_node_module("nodes.marble")
            self.load_node_module("nodes.mx2s")
            self.load_node_module("nodes.vostrokbd")
            
            # Start device listeners
            for dev in [InputDevice(path) for path in list_devices()]:
                if dev.name in self.required_devices:
                    self.add_node("Device:" + dev.name, DeviceReader(dev, self))
            
            # Infinity loop until KeyboardInterrupt is received or the system terminates
            try:
                while True:
                    time.sleep(10000)
            except:
                print("\nTerminating...")
        
        # self.out.close()

        # for consumer in self.consumers.values():
        #     consumer.terminate()

        debug("Bye!")

    def emit(self, topic, package):
        try:
            self.executor.submit(self.process_emit, topic, package)
        except RuntimeError as e:
            warn("Could not emit event, maybe we are shutting down -", e)

    def process_emit(self, topic, package):
        if topic in self.listeners:
            for listener in self.listeners[topic]:
                listener(topic, package)


core = Core()
core.start()
