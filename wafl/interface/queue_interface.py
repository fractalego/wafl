import asyncio
import time

from wafl.interface.base_interface import BaseInterface


class QueueInterface(BaseInterface):
    def __init__(self):
        super().__init__()
        self._bot_has_spoken = False
        self.input_queue = []
        self.output_queue = []

    def output(self, text: str, silent: bool = False):
        if silent:
            self.output_queue.append({"text": text, "silent": True})
            return

        utterance = text
        print(f"Output: {utterance}")
        self.output_queue.append({"text": utterance, "silent": False})
        self._utterances.append((time.time(), f"bot: {text}"))
        self.bot_has_spoken(True)

    async def input(self) -> str:
        while not self.input_queue:
            await asyncio.sleep(0.1)

        text = self.input_queue.pop(0)
        print(f"Input: {text}")
        self._utterances.append((time.time(), f"user: {text}"))
        return text

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken
