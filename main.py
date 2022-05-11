#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from utils import BaseProducer, Context

import importlib
import time
import os

os.nice(-20)

class Core:

    def __init__(self):

        self.out = Context("device_streamer")
        self.consumers = {}
        self.listeners = {}
        self.producers = []

        self.load_device_consumer("marble")
        self.load_device_consumer("mx2s")
        self.load_device_consumer("vostrokbd")
    
    def load_device_consumer(self, name):
        mod = importlib.import_module(name)
        mod.on_init(self)

    def set_consumer(self, device_name, consumer_name):
        
        if not consumer_name in self.consumers:
            print("Can't set consumer. Unknown consumer with name", consumer_name)
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
            for filter_name in self.listeners.keys():
                producer = BaseProducer(filter_name, executor, self.process_event)
                self.producers.append(producer)
                producer.start()
            
            try:
                while True:
                    time.sleep(10000)
                    # print("Leaving in 4s...")
                    # time.sleep(4)
                    # break
            except KeyboardInterrupt:
                pass
            
        self.out.close()

        print("Bye!")

    def process_event(self, device_name, event):
        if device_name in self.listeners:
            self.listeners[device_name].on_event(event)

core = Core()
core.start()

