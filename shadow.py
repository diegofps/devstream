import log


class Shadow:

    def __init__(self, name=None):
        self.name = type(self).__name__ if name is None else name
        self.state_name = f"{self.name}>STATE"
        self.required_devices = set()
        self.reflexes = {}
        self.active = False
        self.mind = None

        log.info(f"Creating shadow name={self.name}")

    def add_reflex(self, reflex):
        assert not reflex.name in self.reflexes, f"Shadow {self.name} already contains a reflex with the name {reflex.name}"

        self.reflexes[reflex.name] = reflex
        reflex.attach(self)

        return reflex
    
    def remove_reflex(self, reflex_name):
        if reflex_name in self.reflexes:
            reflex = self.reflexes[reflex_name]
            del self.reflexes[reflex_name]
            reflex.dettach()

    def require_device(self, device_name):
        self.required_devices.update(device_name)
    
    def attach(self, mind):
        assert not self.is_attached(), "This shadow is already attached to a mind"
        assert not self.is_activated(), "This shadow is already activated"

        log.info(f"Attaching shadow {self.name} to mind")
        self.mind = mind

        self.on_configure()

    def dettach(self):
        assert self.is_attached(), "This shadow is not attached to a mind"

        log.info(f"Dettaching shadow {self.name}")

        if self.is_activated():
            self.deactivate()
        
        self.mind = None
    
    def activate(self):
        log.debug(f"Inside activate for shadow {self.name}")

        assert self.is_attached(), "This shadow is not attached"
        assert not self.is_activated(), "This shadow is already activated"

        self.active = True
        self.mind.add_listener(self.state_name, self.on_state_changed)
        self.mind.require_device(self.required_devices)

        for reflex in self.reflexes.values():
            if reflex.autostart:
                reflex.activate()

        self.on_activate()
    
    def activate_reflex(self, reflex_name, priority):
        log.debug(f"Shifting to reflex {reflex_name} within shadow {self.name} with priority {priority}")
        assert self.is_attached(), "Needs to be attached to use activate_reflex"
        self.mind.emit(self.state_name, reflex_name, priority)
    
    def deactivate(self):
        log.debug(f"Deactivating shadow {self.name}")

        assert self.is_attached(), "This shadow is not attached"
        assert self.is_activated(), "This shadow is not activated"
        
        self.mind.remove_listener(self.state_name, self.on_state_changed)

        for reflex in self.reflexes.values():
            if reflex.is_activated():
                reflex.deactivate()
        
        # TODO: Unrequire devices from mind?
        
        self.active = False
        self.on_deactivate()

    def is_attached(self):
        return self.mind is not None

    def is_activated(self):
        return self.active

    def on_configure(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_state_changed(self, topic_name, event):
        log.info(f"Received an state changed event at shadow {self.name}: topic={topic_name}, event={event}")
        
        for reflex in self.reflexes.values():
            if reflex.name == event:
                if not reflex.is_activated():
                    reflex.activate()
            else:
                if reflex.is_activated():
                    reflex.deactivate()

        # clean = True
        
        # if event[-1] == '*':
        #     event = event[:-1]
        #     clean = False
        
        # if self.active:
        #     if self.name != event:
        #         self.deactivate()
        
        # else:
        #     if self.name == event:
        #         if self.devices_events is not None:
        #             self.add_listener(self.devices_events, self.on_event)
        #         self.clean = clean

        #         self.active = True
        #         self.on_activate()
