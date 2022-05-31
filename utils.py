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

    def __init__(self, core, name):
        self.core = core
        self.name = name

    def start(self):
        self.thread = Thread(target=self.run, name=self.name, daemon=True)
    
    # def emit(self, topic, package):
    #     self.core.emit(topic, package)
