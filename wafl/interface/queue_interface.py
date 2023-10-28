import asyncio
import time

from wafl.interface.base_interface import BaseInterface


class QueueInterface(BaseInterface):
    def __init__(self, output_filter=None):
        super().__init__()
        self._bot_has_spoken = False
        self.input_queue = []
        self.output_queue = []
        self._output_filter = output_filter

    async def output(self, text: str, silent: bool = False):
        if silent:
            self.output_queue.append({"text": text, "silent": True})
            return

        if self._output_filter:
            text = await self._output_filter.filter(
                self.get_utterances_list_with_timestamp(), text
            )

        utterance = text
        self.output_queue.append({"text": utterance, "silent": False})
        self._utterances.append((time.time(), f"bot: {text}"))
        self.bot_has_spoken(True)

    async def input(self) -> str:
        while not self.input_queue:
            await asyncio.sleep(0.1)

        text = self.input_queue.pop(0)
        self._utterances.append((time.time(), f"user: {text}"))
        return text

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken
