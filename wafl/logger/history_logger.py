import hashlib
import os
import time


class LogLevels:
    INFO = 0
    WARNING = 1
    ERROR = 2


class HistoryLogger:
    level = LogLevels

    def __init__(self, interface: "BaseInterface", directory: str = "logs/"):
        if not os.path.exists(directory):
            os.mkdir(directory)

        filename = (
            hashlib.md5(str(time.time()).encode("utf8")).hexdigest() + "-history.log"
        )
        self._filename = os.path.join(directory, filename)
        self._depth = 0
        self._log_level = LogLevels.INFO
        self._interface = interface
        self._max_num_past_utterances = 7
        self._cache = set()

    def set_depth(self, depth: int):
        self._depth = depth

    def set_log_level(self, log_level: LogLevels):
        self._log_level = log_level

    def write(self, text: str, log_level=LogLevels.INFO):
        dialogue = self._interface.get_utterances_list_with_timestamp()[
            -self._max_num_past_utterances :
        ]
        start_time = -1
        if dialogue:
            start_time = dialogue[0][0]

        choices = self._interface.get_choices_and_timestamp()
        facts = self._interface.get_facts_and_timestamp()
        dialogue_items = dialogue + choices + facts
        dialogue_items = sorted(dialogue_items, key=lambda x: x[0])
        dialogue_items = [item[1] for item in dialogue_items if item[0] >= start_time]
        dialogue_items = "\n".join(dialogue_items)
        to_write = f"\n\n<{text}>\n{dialogue_items}\n</{text}>"
        if to_write in self._cache:
            return

        self._cache.add(to_write)
        with open(self._filename, "a") as f:
            f.write(to_write)
