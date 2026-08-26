from devstreamlog import DevStreamLogger
import threading
import importlib
import traceback
import queue
import evdev

log = DevStreamLogger(filename="mind.log")

class Topic:

    def __init__(self, name):
        self.last_event = None
        self.listeners = []
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
        self.thread = threading.Thread(target=self._run, daemon=True)
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
            
            except Exception as err: # pylint: disable=W0718
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

    def __init__(self, name=None):
        self.devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self.name = type(self).__name__ if name is None else name
        self.device_names = {dev.name for dev in self.devices}
        self.topics:dict[str,Topic] = {}
        self.required_devices = set()
        self.executor = Executor()
        self.shadows = {}

    def require_device(self, device_name):
        if isinstance(device_name, (set,list)):
            self.required_devices.update(device_name)
        else:
            self.required_devices.add(device_name)
    
    def add_shadow(self, shadow):
        assert not shadow.name in self.shadows, "A shadow with the same name already exists in the mind"
        self.shadows[shadow.name] = shadow
        shadow.attach(self)
        shadow.activate()
        return shadow
    
    def remove_shadow(self, name):
        shadow = self.shadows.get(name)
        if shadow is not None:
            del self.shadows[name]
            shadow.deactivate()
            shadow.dettach()

    def add_listener(self, topic_names, callback):
        log.debug(f"Adding listener for {topic_names}")
        
        if not isinstance(topic_names, list):
            topic_names = [topic_names]
        
        for topic_name in topic_names:
            if topic_name in self.topics:
                topic = self.topics[topic_name]
                topic.add(callback)
                
                if topic.last_event is not None:
                    self._emit_one(callback, topic_name, topic.last_event)
            
            else:
                topic = Topic(topic_name)
                topic.add(callback)
                self.topics[topic_name] = topic

    def remove_listener(self, topic_names, callback):
        if not isinstance(topic_names, list):
            topic_names = [topic_names]

        for topic_name in topic_names:
            if topic_name in self.topics:
                self.topics[topic_name].remove(callback)

    def emit(self, topic_name, event, priority=100):
        try:
            self.executor.submit(self._emit_all, priority, topic_name, event)
        except RuntimeError as e:
            log.warn("Could not emit event, maybe we are shutting down -", e)

    def run(self):
        try:
            self.executor.wait()
        except:
            log.debug("\nTerminating...")

    def _emit_all(self, topic_name, event):

        if topic_name in self.topics:
            topic:Topic = self.topics[topic_name]
            topic.last_event = event
        
        else:
            topic = Topic(topic_name)
            topic.last_event = event
            self.topics[topic_name] = topic

        if topic_name == "DeviceReader:Logitech MX Master 3S":
            log.debug(f"Topic has {len(topic.listeners)} listeners")
            
        for callback in topic.listeners:
            try:
                # print("Event.topic_name=" + topic_name)
                callback(topic_name, event)
            except Exception as e:
                traceback.print_exc()
                log.error("Error during event processing for topic", topic_name, "- error:", e)

    def _emit_one(self, callback, topic_name, event):
        try:
            callback(topic_name, event)
        except Exception as e:
            traceback.print_exc()
            log.error("Error during event processing for topic", topic_name, "- error:", e)
