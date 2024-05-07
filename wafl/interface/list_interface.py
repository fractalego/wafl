import asyncio
from typing import List

from wafl.interface.base_interface import BaseInterface


class ListInterface(BaseInterface):
    def __init__(self, interfaces_list: List[BaseInterface]):
        super().__init__()
        self._interfaces_list = interfaces_list
        self._synchronize_interfaces()

    async def output(self, text: str, silent: bool = False):
        await asyncio.wait(
            [interface.output(text, silent) for interface in self._interfaces_list],
            return_when=asyncio.ALL_COMPLETED
        )

    async def input(self) -> str:
        done, pending = await asyncio.wait(
            [interface.input() for interface in self._interfaces_list],
            return_when=asyncio.FIRST_COMPLETED
        )
        return done.pop().result()

    def bot_has_spoken(self, to_set: bool = None):
        for interface in self._interfaces_list:
            interface.bot_has_spoken(to_set)

    def _synchronize_interfaces(self):
        for interface in self._interfaces_list:
            interface._utterances = self._utterances