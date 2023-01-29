from importlib import import_module
from inspect import getmembers, isfunction
from typing import List
from wafl.events.BaseEventCreator import BaseEventsCreator


class EventsCreatorFromModuleName(BaseEventsCreator):
    def __init__(self, module_name):
        self._module = {}
        self._functions = {}
        self._module = import_module(module_name)
        self._functions = [item[0] for item in getmembers(self._module, isfunction)]

    def get(self) -> List[str]:
        return [
            eval(f"self._module.{function}()", {"self": self})
            for function in self._functions
        ]
