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

        shadow.add_reflex(self)

        log.info("Starting", self.name, "...")

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
        log.info("Ending", self.name, "...")
        
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
