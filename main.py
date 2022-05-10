#!/usr/bin/env python3

from utils import BaseProducer, Context, load_device_consumer
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

import time
import os

os.nice(-20)

context   = Context("device_streamer")
listeners = defaultdict(list)
producers = []

load_device_consumer("marble", context, listeners)
load_device_consumer("mx2s", context, listeners)

def process_event(device_name, event):
    global listeners
    for listener in listeners[device_name]:
        listener.on_event(event)

with ThreadPoolExecutor(max_workers=1) as executor:

    # Start all producers
    for filter_name in listeners.keys():
        producer = BaseProducer(filter_name, executor, process_event)
        producers.append(producer)
        producer.start()
    
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        pass
    
if context is not None:
    context.close()

print("Bye!")
