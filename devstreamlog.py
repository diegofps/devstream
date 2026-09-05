import logging
import pathlib
import shutil
import os

DEFAULT_LOGGER = None
LOGS_FOLDERPATH = './logs'
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
ENV="PRODUCTION"

class DevStreamLogger:

    def __init__(self, filename="default.log"):
        self.filepath = os.path.join(LOGS_FOLDERPATH, filename)
        self.folderpath = LOGS_FOLDERPATH

        # os.makedirs(LOGS_FOLDERPATH, exist_ok=True)

        handler = logging.FileHandler(self.filepath)
        handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)06d %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S'))

        self.logger = logging.getLogger(self.filepath)
        self.logger.handlers.clear()
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


def init(folderpath=".", max_backups=5, level="DEBUG"):
    global ENV
    ENV = level

    assert max_backups <= 999
    assert max_backups > 0

    folderpath     = pathlib.Path(folderpath).absolute()
    old_folderpath = folderpath.joinpath(f"logs.{max_backups:03d}")

    os.makedirs(folderpath, exist_ok=True)

    if old_folderpath.exists():
        shutil.rmtree(old_folderpath, ignore_errors=True)

    for i in range(max_backups-1,-1,-1):
        new_folderpath = os.path.join(folderpath, f"logs.{i:03d}")
        if os.path.exists(new_folderpath):
            shutil.move(new_folderpath, old_folderpath)
        old_folderpath = new_folderpath

    global LOGS_FOLDERPATH
    LOGS_FOLDERPATH = os.path.join(folderpath, f"logs.{0:03d}")
    os.mkdir(LOGS_FOLDERPATH)


def default_logger():
    global DEFAULT_LOGGER
    if DEFAULT_LOGGER is None:
        DEFAULT_LOGGER = DevStreamLogger()
    return DEFAULT_LOGGER
