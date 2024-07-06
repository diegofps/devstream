import log


class Shadow:

    def __init__(self, mind, lastname=None):
        self.firstname = type(self).__name__
        self.lastname = lastname
        self.name = self.firstname if lastname is None else self.firstname + ":" + lastname
        self.mind = mind
        self.reflexes = {}
        self.on_terminate_listeners = []

        log.info("Starting shadow", self.name, "...")
    
    def add_reflex(self, reflex):
        if reflex.name in self.reflexes:
            log.warn("Reusing reflex name when adding a entry. Removing previous reflex")
            self.remove_reflex(reflex.name)
        
        self.reflexes[reflex.name] = reflex
    
    def remove_reflex(self, reflex_name):
        if reflex_name in self.reflexes:
            reflex = self.reflexes[reflex_name]
            del self.reflexes[reflex_name]
            reflex.on_remove()

    def on_remove(self):
        log.info("Stopping shadow", self.name, "...")

        for reflex in self.reflexes.values():
            reflex.on_remove()
        
        for listener in self.on_terminate_listeners:
            listener(self)

    def require_device(self, device_name):
        self.mind.require_device(device_name)
    
    def set_on_terminate_listener(self, listener):
        self.on_terminate_listeners.append(listener)
