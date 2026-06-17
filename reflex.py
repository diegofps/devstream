from evdev import ecodes as e
from threading import Thread
import traceback
import log

class Daemon(Thread):

    def __init__(self, target):
        super().__init__(target=self.run, daemon=True)
        self.target = target
        self.done = False
    
    def terminate(self):
        self.done = True
    
    def run(self):
        self.target(self)


class Reflex:

    def __init__(self, autostart=False, name=None):
        self.name = type(self).__name__ if name is None else name
        self.must_run_daemon = False
        self.autostart = autostart
        self.devices_events = None
        self.state_topic = None
        self.listeners = []
        self.active = False
        self.daemon = None
        self.shadow = None
        self.mind = None

        log.info("Creating reflex", self.name, "...")
    
    def attach(self, shadow):
        assert not self.is_attached(), f"Attempting to attach a reflex that is already attached"
        log.info(f"Attaching reflex {self.name} to shadow {shadow.name}")
        
        self.mind = shadow.mind
        self.shadow = shadow

        self.on_attach()
        self.on_configure()

    def dettach(self):
        assert self.is_attached(), f"Attempting to dettach a reflex that is not attached"
        log.info(f"Dettaching reflex {self.name} from {self.shadow.name}")

        if self.active:
            self.deactivate()
        
        self.mind = None
        self.shadow = None
        
        self.on_dettach()

    def is_attached(self):
        return self.mind is not None
    
    def is_activated(self):
        return self.active

    def activate(self, *args, **kwargs):
        assert self.is_attached(), f"Attempting to activate a reflex that is not attached"
        assert self.shadow.is_activated(), "Can't start a reflex if its shadow is not activated"

        log.debug(f"Inside activate for reflex {self.name}")

        self.active = True

        for topic_name, callback in self.listeners:
            log.debug(f"Adding listener for topic {topic_name}")
            self.mind.add_listener(topic_name, callback)

        if self.must_run_daemon:
            log.debug(f"Starting daemon at reflex {self.name}")
            self.daemon = Daemon(self.run)
            self.daemon.start()

        self.on_activate(*args, **kwargs)

    def deactivate(self):
        assert self.is_attached(), f"Attempting to deactivate a reflex that is not attached"
        assert self.is_activated(), f"Attempting to deactivate a reflex that is not active"

        log.debug(f"Inside deactivate for reflex {self.name}")

        self.active = False

        if self.daemon is not None:
            log.debug(f"Terminating daemon at reflex {self.name}")
            self.daemon.terminate()
            self.daemon = None
        
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
    
    def shift_reflex(self, reflex_name, *args, **kwargs):
        if self.is_activated():
            self.shadow.shift_reflex(reflex_name, *args, **kwargs)
    
    def debug_event(self, topic_name, evt):
        code  = e.bytype[evt.type][evt.code]
        type  = e.EV[evt.type]
        value = evt.value

        log.debug(f"Processing event: type={type}, code={code}, value={value}")
    
    def on_event(self, topic_name, evt):
        self.debug_event(topic_name, evt)
    
    def on_configure(self):
        # log.debug(f"Inside default on_configure for reflex {self.name}")
        pass

    def on_attach(self):
        # log.debug(f"Inside default on_attach for reflex {self.name}")
        pass

    def on_dettach(self):
        # log.debug(f"Inside default on_dettach for reflex {self.name}")
        pass
    
    def on_activate(self, *args, **kwargs):
        # log.debug(f"Inside default on_activate for reflex {self.name}")
        pass

    def on_deactivate(self):
        # log.debug(f"Inside default on_deactivate for reflex {self.name}")
        pass
    
    def require_daemon(self, value=True):
        # log.debug(f"Inside require_daemon for reflex {self.name}, value={value}")
        self.must_run_daemon = value
    
    def run(self):
        # log.debug(f"Inside default daemon run for reflex {self.name}")
        pass
