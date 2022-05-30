#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from nodes.device_writer import DeviceWriter
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

        self.out = DeviceWriter("devstream")
        self.consumers = {}
        self.listeners = {}
        self.producers = []
        
        self.devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self.device_names = set([dev.name for dev in self.devices])

        self.load_device_consumer("nodes.marble")
        self.load_device_consumer("nodes.mx2s")
        self.load_device_consumer("nodes.vostrokbd")
    
    def load_device_consumer(self, name):
        mod = importlib.import_module(name)
        mod.on_init(self)

    def add_consumer(self, consumer_name, consumer):
        self.consumers[consumer_name] = consumer
    
    def set_consumer(self, device_name, consumer_name):
        
        if isinstance(device_name, list):
            for name in device_name:
                self.set_consumer(name, consumer_name)
            return

        if not consumer_name in self.consumers:
            error("Can't set consumer. Unknown consumer with name", consumer_name)
            return
        
        if not device_name in self.device_names:
            warn("Ignoring listener for missing device", device_name)
            return

        if device_name in self.listeners:
            self.listeners[device_name].on_deactivate()
        
        consumer = self.consumers[consumer_name]
        self.listeners[device_name] = consumer
        consumer.on_activate()

        return consumer

    def start(self):
        
        with ThreadPoolExecutor(max_workers=1) as executor:

            # Start all producers
            devices = [InputDevice(path) for path in list_devices()]
            for d in devices:
                if d.name in self.listeners:
                    producer = DeviceReader(d, executor, self.process_event)
                    self.producers.append(producer)
                    producer.start()

            try:
                while True:
                    time.sleep(10000)
            except:
                print("\nTerminating...")
        
        self.out.close()

        for consumer in self.consumers.values():
            consumer.terminate()

        debug("Bye!")

    def process_event(self, device_name, event):
        if device_name in self.listeners:
            self.listeners[device_name].on_event(device_name, event)


core = Core()
core.start()

