from threading import Thread

import logging


def debug(*args):
    logging.debug(" ".join([str(x) for x in args]))


def info(*args):
    logging.info(" ".join([str(x) for x in args]))


def warn(*args):
    logging.warn(" ".join([str(x) for x in args]))


def error(*args):
    logging.error(" ".join([str(x) for x in args]))


def init_logger(env):

    logging.basicConfig(
        level=logging.INFO if env == "PRODUCTION" else logging.DEBUG, 
        filename="main.log", 
        filemode="w", 
        format='%(name)s - %(levelname)s - %(message)s' 
    )

    info("Starting in", env, "environment")


def smooth(v):
    return int(v * 1.5)


class BaseNode:

    def __init__(self, core, lastname=None):
        self.firstname = type(self).__name__
        self.lastname = lastname
        self.name = self.firstname if lastname is None else self.firstname + ":" + lastname
        self.thread = None
        self.core = core
        self.done = False
        
        info("Starting", self.name, "...")

    def start(self):
        self.thread = Thread(target=self._call_run, name=self.name, daemon=True)
        self.thread.start()
    
    def _call_run(self):
        try:
            info(self.name, "started")
            self.done = False
            self.run()
            info(self.name, "ended")
        except Exception as e:
            error(self.name, "- Failure during thread execution -", e)

    def terminate(self):
        self.done = True
    