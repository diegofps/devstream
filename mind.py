from concurrent.futures import ThreadPoolExecutor
from shadow import Shadow

import threading
import importlib
import traceback
import queue
import evdev
import time
import log


class Topic:

    def __init__(self, name):
        self.listeners = []
        self.last_event = None
        self.name = name
    
    def add(self, callback):
        self.listeners.append(callback)
    
    def remove(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

class Job:

    def __init__(self, id, callback, priority, args):
        self.callback = callback
        self.priority = priority
        self.args = args
        self.id = id

    def __lt__(self, other):
        if other.priority is None:
            return False
        elif self.priority != other.priority:
            return self.priority < other.priority
        else:
            return self.id < other.id
        

class Executor:

    def __init__(self):
        self.thread = threading.Thread(target=self._run)
        self.priority_queue = queue.PriorityQueue()
        self.lock = threading.Lock()
        self.lock.acquire()
        self.next_job_id = 0
        self.done = False

        self.thread.start()

    def _run(self):
        while not self.done:
            job:Job = self.priority_queue.get()

            if job.callback is None:
                break

            try:
                job.callback(*job.args)
            except Exception as err:
                log.error("Something happened when processing a Mind's callback event:", err)
                traceback.print_exc()
        
        self.lock.release()

    def submit(self, callback, priority, *args):
        job = Job(self.next_job_id, callback, priority, args)
        self.priority_queue.put(job)
        self.next_job_id += 1

    def terminate(self):
        self.done = True
        self.priority_queue.put(Job(self.next_job_id, None, None, None))
        self.next_job_id += 1
    
    def wait(self):
        self.lock.acquire()
        self.lock.release()

class Mind:

    def __init__(self):

        self.shadows = {}
        self.topics = {}
        
        self.devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self.device_names = set([dev.name for dev in self.devices])
        self.required_devices = set()

    def require_device(self, device_name):
        if isinstance(device_name, list):
            for name in device_name:
                self.require_device(name)
        else:
            self.required_devices.add(device_name)
    
    def add_shadow(self, shadow_name, *args):
        if shadow_name in self.shadows:
            log.warn("Shadow is already added, skipping -", shadow_name)
            return
        
        shadow = Shadow(self, shadow_name)
        mod = importlib.import_module("shadows." + shadow_name)
        mod.on_load(shadow, *args)
        self.shadows[shadow.name] = shadow

        log.info(f"{shadow_name} was added to the mind.")

        return shadow
    
    def remove_shadow(self, shadow_name):
        # log.debug("Removing shadow", shadow_name)
        
        if not shadow_name in self.shadows:
            log.warn("Attempting to remove a shadow that is not loaded", shadow_name)
            return
        
        shadow = self.shadows.get(shadow_name)

        if shadow is not None:
            del self.shadows[shadow_name]
            shadow.on_remove()
        
        log.info(f"{shadow_name} was removed from the mind.")

    def _add_listener(self, topic_name, callback):
        
        if isinstance(topic_name, list):
            for name in topic_name:
                self._add_listener(name, callback)
            return
        
        # Register this listener in the corresponding topic

        if not topic_name in self.topics:
            topic = Topic(topic_name)
            topic.add(callback)
            self.topics[topic_name] = topic
        
        else:
            topic:Topic = self.topics[topic_name]
            topic.add(callback)

            if topic.last_event is not None:
                self._emit_one(callback, topic_name, topic.last_event)

    def _remove_listener(self, topic_name, callback):
    
        if isinstance(topic_name, list):
            for name in topic_name:
                self._remove_listener(name, topic_name)
            return

        # Remove it if there is a topic name with this name 
        # and the listener is there.

        if topic_name in self.topics:
            topic = self.topics[topic_name]
            topic.remove(callback)

    def emit(self, topic_name, event, priority=100):
        if topic_name in self.topics:
            topic:Topic = self.topics[topic_name]
            topic.last_event = event
        
        else:
            topic = Topic(topic_name)
            topic.last_event = event
            self.topics[topic_name] = topic

        try:
            self.executor.submit(self._emit_all, priority, topic_name, event)
        except RuntimeError as e:
            log.warn("Could not emit event, maybe we are shutting down -", e)

    def _emit_all(self, topic_name, event):
        if topic_name in self.topics:
            topic = self.topics[topic_name]

            # log.info("Calling listeners", str(topic.listeners))

            for callback in topic.listeners:
                try:
                    callback(topic_name, event)
                except Exception as e:
                    traceback.print_exc()
                    log.error("Error during event processing for topic", topic_name, "- error:", e)

    def _emit_one(self, callback, topic_name, event):
        try:
            callback(topic_name, event)
        except Exception as e:
            import traceback
            traceback.print_exc()
            log.error("Error during event processing for topic", topic_name, "- error:", e)

    def start(self):

        self.executor = Executor()

        # Output shadows

        self.add_shadow("virtual_keyboard")
        self.add_shadow("virtual_mouse")
        self.add_shadow("virtual_pen")

        # Input shadows

        self.add_shadow("logitech_marble")
        self.add_shadow("vostro_keyboard")
        self.add_shadow("basic_keyboards")
        self.add_shadow("macro_keyboard")
        self.add_shadow("logitech_mx2s")
        self.add_shadow("xppen_deco_pro")

        # System shadows

        self.add_shadow("dispatcher")
        self.add_shadow("watch_login")
        self.add_shadow("watch_devices")
        # self.add_shadow("watch_disks")
        
        # Logic shadows

        self.add_shadow("smart_output")

        # Infinity loop until KeyboardInterrupt is received or the system terminates

        try:
            self.executor.wait()
            
        except:
            print("\nTerminating...")
        
        log.debug("Bye!")
