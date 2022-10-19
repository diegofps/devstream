from evdev import ecodes as e
from threading import Thread
import log


class Reflex:

    def __init__(self, shadow, lastname=None):

        self.lastname = lastname
        self.firstname = type(self).__name__
        self.name = self.firstname if lastname is None else self.firstname + ":" + lastname

        self.mind = shadow.mind
        self.shadow = shadow
        self.listeners = []
        self.thread = None
        self.done = False

        self.devices_events = None
        self.state_topic = None

        shadow.add_reflex(self)

        log.info("Starting reflex", self.name, "...")

    def start(self):
        self.thread = Thread(target=self._call_run, name=self.name, daemon=True)
        self.thread.start()
    
    def _call_run(self):

        try:
            # log.info(self.name, "started")
            self.done = False
            self.run()
        except Exception as e:
            log.error(self.name, "- Failure during thread execution -", e)


    def terminate(self):
        self.done = True
    
    def on_remove(self):
        log.info("Stopping reflex", self.name, "...")
        
        self.terminate()

        for topic_name, callback in self.listeners:
            self.mind.remove_listener(topic_name, callback)
        
        self.listeners = []
    
    def add_listener(self, topic_name, callback):
        self.listeners.append((topic_name, callback))
        self.mind._add_listener(topic_name, callback)
        # log.debug(self.name, "add_listener", topic_name)
    
    def remove_listener(self, topic_name, callback):
        try:
            # log.debug(self.name, "remove_listener", topic_name)
            self.mind._remove_listener(topic_name, callback)
            self.listeners.remove((topic_name, callback))
        except ValueError:
            # log.warn("Attempting to remove a topic callback that is not present")
            pass

    def configure_states(self, state_topic, devices_events):
        self.devices_events = devices_events
        self.state_topic = state_topic
        self.add_listener(state_topic, self.on_state_changed)
    
    def on_state_changed(self, topic_name, event):
        clean = True
        
        if event[-1] == '*':
            event = event[:-1]
            clean = False
        
        if self.name == event:
            if self.devices_events is not None:
                self.add_listener(self.devices_events, self.on_event)
            self.clean = clean

            if not self.active:
                self.active = True
                self.on_activate()

        else:
            if self.active:
                self.active = False
                self.on_deactivate()
            
            if self.devices_events is not None:
                self.remove_listener(self.devices_events, self.on_event)

    def on_event(self, topic_name, evt):
        # if evt.code in [e.ABS_TILT_X, e.ABS_TILT_Y, e.ABS_X, e.ABS_Y, e.ABS_PRESSURE]:
        #     return 
        
        code  = e.bytype[evt.type][evt.code]
        type  = e.EV[evt.type]
        value = evt.value

        log.debug(f"Processing event: type={type}, code={code:20}, value={value}")
        
        
    def on_activate(self):
        pass

    def on_deactivate(self):
        pass
    