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
