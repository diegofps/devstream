import logging
import os

DEFAULT_LOGGER = None
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
ENV="PRODUCTION"

class DevStreamLogger:

    def __init__(self, filename="default.log", folderpath="./logs"):
        self.filepath = os.path.join(folderpath, filename)
        self.folderpath = folderpath

        os.makedirs(folderpath, exist_ok=True)

        handler = logging.FileHandler(self.filepath)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

        self.logger = logging.getLogger(self.filepath)
        self.logger.setLevel(logging.INFO if ENV == "PRODUCTION" else logging.DEBUG)
        self.logger.addHandler(handler)

    def debug(self, *args, **kwargs):
        self._commit(self.logger.debug, *args, **kwargs)

    def info(self, *args, **kwargs):
        self._commit(self.logger.info, *args, **kwargs)

    def warn(self, *args, **kwargs):
        self._commit(self.logger.warning, *args, **kwargs)

    def error(self, *args, **kwargs):
        self._commit(self.logger.error, *args, **kwargs)

    def _commit(self, target, *args, **kwargs):
        title = " ".join([str(x) for x in args])

        if kwargs:
            params = [f"  {k}={v}" for k,v in kwargs.items()]
            params = "\n".join([x for x in params])
            title = title + ':\n' + params
        
        target(title)


def clear_logs(folderpath="./logs"):
    pattern = os.path.join(folderpath, '*.log')
    cmd = f"rm \"{pattern}\""
    # print(cmd)
    os.system(cmd)

def set_log_level(level):
    global ENV
    ENV = level


def default_logger():
    global DEFAULT_LOGGER
    if DEFAULT_LOGGER is None:
        DEFAULT_LOGGER = DevStreamLogger()
    return DEFAULT_LOGGER
