from typing import List, Any
from wafl.events.BaseEventCreator import BaseEventsCreator


class EventsCreatorFromFunctionList(BaseEventsCreator):
    def __init__(self, functions: List[Any]):
        self._functions = functions

    def get(self) -> List[str]:
        return [function() for function in self._functions]
