from typing import List

from wafl.interface.base_interface import BaseInterface


class ListInterface(BaseInterface):
    def __init__(self, interfaces_list: List[BaseInterface]):
        super().__init__()
        self._interfaces_list = interfaces_list

    async def output(self, text: str, silent: bool = False):
        for interface in self._interfaces_list:
            await interface.output(text, silent)

    async def input(self) -> str:
        for interface in self._interfaces_list:
            if interface.is_listening():
                text = await interface.input()
                if text:
                    return text

        return ""

    def bot_has_spoken(self, to_set: bool = None):
        for interface in self._interfaces_list:
            interface.bot_has_spoken(to_set)
