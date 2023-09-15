import time

from typing import List


class BaseInterface:
    def __init__(self, decorator=None):
        self._is_listening = True
        self._choices = []
        self._facts = []
        self._utterances = []
        self._decorator = decorator

    async def output(self, text: str, silent: bool = False):
        raise NotImplementedError

    async def input(self) -> str:
        raise NotImplementedError

    def bot_has_spoken(self, to_set: bool = None):
        raise NotImplementedError

    def is_listening(self):
        return self._is_listening

    def activate(self):
        self._is_listening = True

    def deactivate(self):
        self._is_listening = False
        self._choices = []
        self._facts = []
        self._utterances = []

    def add_hotwords(self, hotwords: List[str]):
        raise NotImplementedError

    async def add_choice(self, text):
        self._choices.append((time.time(), text))
        await self.output(f"Making the choice: {text}", silent=True)

    async def add_fact(self, text):
        self._facts.append((time.time(), text))
        await self.output(f"{text}", silent=True)

    def get_choices_and_timestamp(self):
        return self._choices

    def get_facts_and_timestamp(self):
        return self._facts

    def get_utterances_list(self):
        return [item[1] for item in self._utterances]

    def get_utterances_list_with_timestamp(self):
        return self._utterances

    def reset_history(self):
        self._utterances = []
        self._choices = []
        self._facts = []

    def _decorate_reply(self, text: str) -> str:
        if not self._decorator:
            return text

        return self._decorator.extract(text, self._utterances)
