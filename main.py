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
        self.package_lifecycles = {}
        self.node_lifecycles = {}

    def require_device(self, device_name):
        if isinstance(device_name, list):
            for name in device_name:
                self.require_device(name)
        else:
            self.required_devices.add(device_name)
    
    def load_package(self, name, *args):
        mod = importlib.import_module("nodes." + name)
        mod.on_load(self, *args)
    
    def unload_package(self, name, *args):
        mod = importlib.import_module(name)
        mod.on_unload(self, *args)
        # TODO: Remove nodes in this package_lifecycle

    def add_node(self, node):
        if node.name in self.nodes:
            warn("Reusing name when adding a node. Removing previous node")
            self.remove_node(node.name)
        
        self.nodes[node.name] = node
        # TODO: Add this node to its package_lifecycle (new  parameter)
    
    def remove_node(self, node_name):
        if node_name in self.nodes:
            # node = self.nodes[node_name]
            del self.nodes[node_name]

        if node_name in self.node_lifecycles:
            pairs = self.node_lifecycles[node_name]
            del self.node_lifecycles[node_name]

            for topic_name, callback in pairs:
                if topic_name in self.listeners:
                    listeners = self.listeners[topic_name]

                    if callback in listeners:
                        listeners.remove(callback)

    def register_listener(self, lifecycle_node, topic_name, callback):
        
        if isinstance(topic_name, list):
            for name in topic_name:
                self.register_listener(lifecycle_node, name, callback)
            return
        
        # Register this listener in the corresponding listeners list
        if not topic_name in self.listeners:
            self.listeners[topic_name] = [callback]
        
        else:
            self.listeners[topic_name].append(callback)
        
        # Register this listener in the context given. If the node 
        # is later removed all its listeners will be removed
        node_name = lifecycle_node.name
        pair = (topic_name, callback)

        if node_name in self.node_lifecycles:
            self.node_lifecycles[node_name].append(pair)

        else:
            self.node_lifecycles[node_name] = [pair]

    def unregister_listener(self, lifecycle_node, topic_name, callback):
    
        if isinstance(topic_name, list):
            for name in topic_name:
                self.unregister_listener(name, topic_name)
            return

        # If there is a topic name with this name and the 
        # listener is there remove it
        if topic_name in self.listeners:
            listeners = self.listeners[topic_name]

            if callback in listeners:
                listeners.remove(callback)
    
        # If this listener is registered in the corresponding lifecycle, 
        # remove it as well
        node_name = lifecycle_node.name

        if node_name in self.node_lifecycles:
            listeners = self.node_lifecycles[node_name]
            pair = (topic_name, callback)

            if pair in listeners:
                listeners.remove(pair)

    def start(self):

        with ThreadPoolExecutor(max_workers=1) as executor:
            self.executor = executor

            # Virtual nodes
            self.load_package("device_writer")
            self.load_package("watch_login")
            self.load_package("dispatcher")
            # self.load_package("watch_windows")
            # self.load_package("watch_disks")
            # self.load_package("watch_devices")

            self.load_package("logitech_marble")
            self.load_package("logitech_mx2s")
            self.load_package("vostro_keyboard")
            self.load_package("basic_keyboards")
            self.load_package("macro_keyboard")
            
            # Physical nodes
            for dev in [InputDevice(path) for path in list_devices()]:
                if dev.name in self.required_devices:
                    self.load_package(self, dev)
            
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
