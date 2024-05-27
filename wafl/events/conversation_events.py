import os
import re

from wafl.events.answerer_creator import create_answerer
from wafl.simple_text_processing.normalize import normalized
from wafl.config import Configuration
from wafl.events.utils import input_is_valid, load_knowledge
from wafl.simple_text_processing.questions import is_question
from wafl.exceptions import InterruptTask

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


class ConversationEvents:
    def __init__(
        self,
        config: "Configuration",
        interface: "BaseInterface",
        logger=None,
    ):
        self._config = config
        self._knowledge = load_knowledge(config, logger)
        self._answerer = create_answerer(config, self._knowledge, interface, logger)
        self._answerer._client._connector._cache = {}
        self._interface = interface
        self._logger = logger
        self._is_computing = False
        if logger:
            self._logger.set_depth(0)

    async def output(self, text: str):
        await self._interface.output(text)

    async def _process_query(self, text: str):
        self._is_computing = True
        self._interface.bot_has_spoken(False)
        if not input_is_valid(text):
            self._is_computing = False
            return False

        text_is_question = is_question(text)
        try:
            answer = await self._answerer.answer(text)

        except InterruptTask:
            await self._interface.output("Task interrupted")
            self._is_computing = False
            return False

        if not self._interface.bot_has_spoken():
            if not text_is_question and not answer.is_neutral():
                await self.output(answer.text)

            if text_is_question and answer.text not in ["True", "False"]:
                await self.output(answer.text)

            if text_is_question and answer.is_false():
                await self.output("I don't know")

            if (
                not text_is_question
                and self._interface.get_utterances_list()
                and self._interface.last_speaker() == "user"
            ):
                await self._interface.output("I don't know what to reply")

            if (
                not text_is_question
                and answer.is_true()
                and not self._interface.bot_has_spoken()
            ):
                await self._interface.output("Yes")

        self._is_computing = False
        return answer

    async def process_next(self, activation_word: str = "") -> bool:
        try:
            text = await self._interface.input()
            text = text.replace("'", r"\'")

        except IndexError:
            return False

        if (
            activation_word
            and not self._interface.is_listening()
            and self._activation_word_in_text(activation_word, text)
        ):
            self._interface.activate()
            self._logger.set_depth(0)
            self._logger.write(f"Activation word found {text}")
            if normalized(text) == normalized(activation_word, lower_case=True):
                return True

        text = self.__remove_activation_word_and_normalize(activation_word, text)
        if self._interface.is_listening():
            answer = await self._process_query(text)
            if answer and not answer.is_false():
                return True

        return False

    def is_computing(self):
        return self._is_computing

    def reload_knowledge(self):
        self._knowledge = load_knowledge(self._config, self._logger)

    def reset_discourse_memory(self):
        self._answerer = create_answerer(
            self._config, self._knowledge, self._interface, self._logger
        )

    def _activation_word_in_text(self, activation_word, text):
        if f"[{normalized(activation_word)}]" in normalized(text):
            return True

        return False

    def __remove_activation_word_and_normalize(self, activation_word, text):
        to_remove = f"[{activation_word}]"
        text = text.replace(to_remove, "").strip()
        text = re.sub(f"^{activation_word}", "", text, flags=re.IGNORECASE)
        return text
