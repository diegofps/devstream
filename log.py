import logging

def _commit(target, *args, **kwargs):
    title = " ".join([str(x) for x in args])
    if kwargs:
        params = [f"  {k}={v}" for k,v in kwargs.items()]
        params = "\n".join([x for x in params])
        target(title + ':\n' + params)
    else:
        target(title)

def debug(*args, **kwargs):
    _commit(logging.debug, *args, **kwargs)


def info(*args, **kwargs):
    _commit(logging.info, *args, **kwargs)


def warn(*args, **kwargs):
    _commit(logging.warn, *args, **kwargs)


def error(*args, **kwargs):
    _commit(logging.error, *args, **kwargs)


def init_logger(env):

    logging.basicConfig(
        level=logging.INFO if env == "PRODUCTION" else logging.DEBUG, 
        filename="main.log", 
        filemode="w", 
        format='%(name)s - %(levelname)s - %(message)s' 
    )

    info("Starting in", env, "environment")
