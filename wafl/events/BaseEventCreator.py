from typing import List


class BaseEventsCreator:
    def get(self) -> List[str]:
        raise NotImplementedError
