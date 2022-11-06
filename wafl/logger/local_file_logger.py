import hashlib
import os.path
import time

from wafl.logger.base_logger import LogLevels, BaseLogger


class LocalFileLogger(BaseLogger):
    def __init__(self, directory: str = "logs/"):
        if not os.path.exists(directory):
            os.mkdir(directory)

        filename = hashlib.md5(str(time.time()).encode("utf8")).hexdigest() + ".log"
        self._filename = os.path.join(directory, filename)
        self._depth = 0
        self._log_level = LogLevels.INFO

    def set_depth(self, depth: int):
        self._depth = depth

    def set_log_level(self, log_level: LogLevels):
        self._log_level = log_level

    def write(self, text: str, log_level=LogLevels.INFO):
        with open(self._filename, "a") as file:
            if log_level >= self._log_level:
                file.write(" " * self._depth + text + "\n")
                file.flush()
