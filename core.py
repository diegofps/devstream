from concurrent.futures import ThreadPoolExecutor
from evdev import list_devices, InputDevice
from deploy import Deploy

import importlib
import evdev
import time
import log


class Topic:

    def __init__(self, name):
        self.listeners = []
        self.value = None
        self.name = name
    
    def add(self, callback):
        self.listeners.append(callback)
    
    def remove(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)


class Core:

    def __init__(self):

        self.deploys = {}
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
    
    def add_deploy(self, deploy_name, *args):
        if deploy_name in self.deploys:
            log.warn("Deploy is already added, skipping -", deploy_name)
            return
        
        deploy = Deploy(self, deploy_name)
        mod = importlib.import_module("deploys." + deploy_name)
        mod.on_load(deploy, *args)
        self.deploys[deploy.name] = deploy
    
    def remove_deploy(self, deploy_name):
        deploy = self.deploys.get(deploy_name)
        if deploy is not None:
            del self.deploys[deploy_name]
            deploy.on_remove()

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
            topic = self.topics[topic_name]
            topic.add(callback)

            if topic.value is not None:
                self._emit_one(callback, topic_name, topic.value)

    def _remove_listener(self, topic_name, callback):
    
        if isinstance(topic_name, list):
            for name in topic_name:
                self._remove_listener(name, topic_name)
            return

        # If there is a topic name with this name and the 
        # listener is there remove it
        if topic_name in self.topics:
            topic = self.topics[topic_name]
            topic.remove(callback)

    def emit(self, topic_name, event):
        if topic_name in self.topics:
            topic = self.topics[topic_name]
            topic.value = event
        else:
            topic = Topic(topic_name)
            topic.value = event
            self.topics[topic_name] = topic

        try:
            self.executor.submit(self._emit_all, topic_name, event)
        except RuntimeError as e:
            log.warn("Could not emit event, maybe we are shutting down -", e)

    def _emit_all(self, topic_name, event):
        if topic_name in self.topics:
            topic = self.topics[topic_name]
            for callback in topic.listeners:
                try:
                    callback(topic_name, event)
                except Exception as e:
                    log.error("Error during event processing for topic", topic_name, "- error:", e)

    def _emit_one(self, callback, topic_name, event):
        try:
            callback(topic_name, event)
        except Exception as e:
            log.error("Error during event processing for topic", topic_name, "- error:", e)

    def start(self):

        with ThreadPoolExecutor(max_workers=1) as executor:
            self.executor = executor

            # Virtual nodes
            self.add_deploy("device_writer")
            self.add_deploy("watch_login")
            self.add_deploy("dispatcher")
            # self.add_deploy("watch_disks")
            # self.add_deploy("watch_devices")

            self.add_deploy("logitech_marble")
            self.add_deploy("vostro_keyboard")
            self.add_deploy("basic_keyboards")
            self.add_deploy("macro_keyboard")
            self.add_deploy("logitech_mx2s")
            
            # Physical nodes
            for dev in [InputDevice(path) for path in list_devices()]:
                if dev.name in self.required_devices:
                    self.add_deploy("device_reader", dev)
            
            # Infinity loop until KeyboardInterrupt is received or the system terminates
            try:
                while True:
                    time.sleep(10000)
            except:
                print("\nTerminating...")
            
            # for node in self.nodes.values():
            #     node.terminate()
        
        log.debug("Bye!")
