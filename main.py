#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from nodes.device_reader import DeviceReader
from evdev import list_devices, InputDevice
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
        if isinstance(device_name, list):
            for name in device_name:
                self.require_device(name)
        else:
            self.required_devices.add(device_name)
    
    def load_package(self, name, *args):
        mod = importlib.import_module(name)
        mod.on_init(self, *args)

    def add_node(self, consumer_name, consumer):
        self.nodes[consumer_name] = consumer
    
    def register_listener(self, topic_name, callback):
        
        if isinstance(topic_name, list):
            for name in topic_name:
                self.register_listener(name, topic_name)
        
        elif not topic_name in self.listeners:
            self.listeners[topic_name] = [callback]
        
        else:
            self.listeners[topic_name].append(callback)

    def unregister_listener(self, topic_name, callback):
    
        if isinstance(topic_name, list):
            for name in topic_name:
                self.unregister_listener(name, topic_name)

        elif topic_name in self.listeners:
            listeners = self.listeners[topic_name]
            if callback in listeners:
                listeners.remove(callback)
    

    def start(self):

        with ThreadPoolExecutor(max_workers=1) as executor:
            self.executor = executor

            # Virtual nodes
            self.load_package("nodes.device_writer")
            self.load_package("nodes.watch_windows")
            # self.load_package("nodes.watch_disks")
            # self.load_package("nodes.watch_devices")

            self.load_package("nodes.logitech_marble")
            self.load_package("nodes.logitech_mx2s")
            self.load_package("nodes.vostro_keyboard")
            self.load_package("nodes.basic_keyboards")
            self.load_package("nodes.macro_keyboard")
            
            # Physical nodes
            for dev in [InputDevice(path) for path in list_devices()]:
                if dev.name in self.required_devices:
                    self.add_node("Device:" + dev.name, DeviceReader(dev, self))
            
            # Infinity loop until KeyboardInterrupt is received or the system terminates
            try:
                while True:
                    time.sleep(10000)
            except:
                print("\nTerminating...")
            
            for node in self.nodes.values():
                node.terminate()
        
        debug("Bye!")

    def emit(self, topic_name, package):
        try:
            self.executor.submit(self.process_emit, topic_name, package)
        except RuntimeError as e:
            warn("Could not emit event, maybe we are shutting down -", e)

    def process_emit(self, topic, package):
        if topic in self.listeners:
            for listener in self.listeners[topic]:
                try:
                    listener(topic, package)
                except Exception as e:
                    error("Error during event processing for topic", topic, "- error:", e)


core = Core()
core.start()
