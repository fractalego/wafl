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
            return_when=asyncio.ALL_COMPLETED,
        )

    async def input(self) -> str:
        done, pending = await asyncio.wait(
            [interface.input() for interface in self._interfaces_list],
            return_when=asyncio.FIRST_COMPLETED,
        )
        return done.pop().result()

    async def insert_input(self, text: str):
        await asyncio.wait(
            [interface.insert_input(text) for interface in self._interfaces_list],
            return_when=asyncio.ALL_COMPLETED,
        )

    def bot_has_spoken(self, to_set: bool = None):
        if to_set == None:
            return all(
                interface.bot_has_spoken() for interface in self._interfaces_list
            )

        for interface in self._interfaces_list:
            interface.bot_has_spoken(to_set)

    def activate(self):
        for interface in self._interfaces_list:
            interface.activate()
        super().activate()

    def deactivate(self):
        for interface in self._interfaces_list:
            interface.deactivate()
        super().deactivate()
        self._synchronize_interfaces()

    def add_hotwords(self, hotwords):
        for interface in self._interfaces_list:
            interface.add_hotwords(hotwords)

    def _synchronize_interfaces(self):
        for interface in self._interfaces_list:
            interface._utterances = self._utterances
