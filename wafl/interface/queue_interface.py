import asyncio

from wafl.interface.base_interface import BaseInterface


class QueueInterface(BaseInterface):
    def __init__(self):
        super().__init__()
        self._bot_has_spoken = False
        self.input_queue = []
        self.output_queue = []

    async def output(self, text: str, silent: bool = False):
        if silent:
            self.output_queue.append({"text": text, "silent": True})
            return

        self.output_queue.append({"text": text, "silent": False})
        self._insert_utterance(speaker="bot", text=text)
        self.bot_has_spoken(True)

    async def input(self) -> str:
        while not self.input_queue:
            await asyncio.sleep(0.1)

        text = self.input_queue.pop(0)
        self._insert_utterance(speaker="user", text=text)
        return text

    async def insert_input(self, text: str):
        self.input_queue.append(text)

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken
