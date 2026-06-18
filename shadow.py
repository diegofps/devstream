import log


class Shadow:

    def __init__(self, name=None):
        self.name = type(self).__name__ if name is None else name
        self.state_name = f"{self.name}>STATE"
        self.required_devices = set()
        self.reflexes = {}
        self.active = False
        self.mind = None

        log.info(f"Creating shadow {self.name}")

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
            if reflex.autostart or reflex.keepalive:
                log.debug(f"Shadow {self.name} is activating reflex {reflex.name}")
                reflex.activate()

        self.on_activate()
    
    def shift_reflex(self, reflex_name, *args, **kwargs):
        log.debug(f"Shifting to reflex {reflex_name}, args={args}m kwargs={kwargs} within shadow {self.name}")
        assert self.is_attached(), "Needs to be attached to use activate_reflex"
        self.mind.emit(self.state_name, (reflex_name, args, kwargs), 50)
    
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

        reflex_name, args, kwargs = event
        target_reflex = None

        for reflex in self.reflexes.values():
            if reflex.name == reflex_name:
                target_reflex = reflex
                break
        
        if target_reflex is None:
            log.warn(f"Shadow {self.name} if trying to shift reflexes but couldn't find the target reflex {reflex_name}, args={args}, kwargs={kwargs}")

        elif target_reflex.is_activated():
            log.warn(f"Shadow {self.name} if trying to shift reflexes but the target reflex {reflex_name} is already activated, args={args}, kwargs={kwargs}")
        
        else:
            for reflex in self.reflexes.values():
                if reflex != target_reflex and not reflex.keepalive:
                    if reflex.is_activated():
                        reflex.deactivate()
            
            target_reflex.activate(*args, **kwargs)
        