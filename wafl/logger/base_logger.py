class LogLevels:
    INFO = 0
    WARNING = 1
    ERROR = 2


class BaseLogger:
    level = LogLevels

    def set_depth(self, depth: int):
        raise NotImplementedError()

    def set_log_level(self, log_level: LogLevels):
        raise NotImplementedError()

    def write(self, text: str, log_level=LogLevels.INFO):
        raise NotImplementedError
