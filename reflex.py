from evdev import ecodes as e
from threading import Thread
import traceback
import log


class Reflex:

    def __init__(self, name=None):
        self.name = type(self).__name__ if name is None else name
        self.mind = None
        self.shadow = None
        self.listeners = []
        self.active = False
        self.devices_events = None
        self.state_topic = None

        log.info("Starting reflex", self.name, "...")
    
    def attach(self, shadow):
        assert not self.is_attached(), f"Attempting to attach a reflex that is already attached"
        log.info("Attaching reflex", self.name, "...")
        
        self.mind = shadow.mind
        self.shadow = shadow

        self.on_attach()
        self.on_configure()

    def dettach(self):
        assert self.is_attached(), f"Attempting to dettach a reflex that is not attached"
        log.info("Dettaching reflex", self.name, "...")

        if self.active:
            self.deactivate()
        
        self.mind = None
        self.shadow = None
        
        self.on_dettach()

    def is_attached(self):
        return self.mind is not None
    
    def is_activated(self):
        return self.active

    def activate(self):
        assert self.is_attached(), f"Attempting to activate a reflex that is not attached"
        log.debug(f"Inside Reflex::activate")

        self.active = True

        for topic_name, callback in self.listeners:
            log.debug(f"Adding listener for topic {topic_name}")
            self.mind.add_listener(topic_name, callback)

        log.debug(f"Calling on_activate")
        self.on_activate()
        log.debug(f"Leaving Reflex::activate")

    def deactivate(self):
        assert self.is_attached(), f"Attempting to deactivate a reflex that is not attached"
        assert self.is_activated(), f"Attempting to deactivate a reflex that is not active"

        self.active = False
        
        for topic_name, callback in self.listeners:
            self.mind.remove_listener(topic_name, callback)

        self.on_deactivate()
    
    def add_listener(self, topic_names, callback):
        if not isinstance(topic_names, list):
            topic_names = [topic_names]
        
        for topic_name in topic_names:
            self.listeners.append((topic_name, callback))
        
    def remove_listener(self, topic_names, callback):
        if not isinstance(topic_names, list):
            topic_names = [topic_names]
        
        for topic_name in topic_names:
            try:
                self.listeners.remove((topic_name, callback))
            except ValueError:
                traceback.print_stack()
                log.debug("Attempting to remove a topic callback that is not present", topic_name=topic_name, listener=self.name)
                pass
    
    def debug_event(self, topic_name, evt):
        code  = e.bytype[evt.type][evt.code]
        type  = e.EV[evt.type]
        value = evt.value

        log.debug(f"Processing event: type={type}, code={code}, value={value}")
    
    def on_event(self, topic_name, evt):
        self.debug_event(topic_name, evt)
    
    def on_configure(self):
        pass

    def on_attach(self):
        pass

    def on_dettach(self):
        pass
    
    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
    