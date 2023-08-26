import os
import re

from wafl.events.answerer_creator import create_answerer
from wafl.policy.answerer_policy import AnswerPolicy
from wafl.simple_text_processing.normalize import normalized
from wafl.config import Configuration
from wafl.events.utils import input_is_valid, remove_text_between_brackets
from wafl.simple_text_processing.questions import is_question
from wafl.exceptions import InterruptTask

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


class ConversationEvents:
    def __init__(
        self,
        knowledge: "BaseKnowledge",
        interface: "BaseInterface",
        code_path=None,
        config=None,
        logger=None,
    ):
        if not config:
            config = Configuration.load_local_config()

        self._answerer = create_answerer(
            config, knowledge, interface, code_path, logger
        )
        self._knowledge = knowledge
        self._interface = interface
        self._policy = AnswerPolicy(config, interface, logger)
        self._logger = logger
        if logger:
            self._logger.set_depth(0)

    async def output(self, text: str):
        await self._interface.output(text)

    async def _process_query(self, text: str):
        self._interface.bot_has_spoken(False)

        if not input_is_valid(text):
            return False

        text_is_question = is_question(text)
        self._policy.improvise = False
        try:
            answer = await self._answerer.answer(
                remove_text_between_brackets(text), policy=self._policy
            )

        except InterruptTask:
            await self._interface.output("Task interrupted")
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
                and answer.is_false()
                and not self._interface.bot_has_spoken()
            ):
                await self._interface.output("I don't know what to reply")

            if (
                not text_is_question
                and answer.is_true()
                and not self._interface.bot_has_spoken()
            ):
                await self._interface.output("Yes")

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

    def _activation_word_in_text(self, activation_word, text):
        if f"[{normalized(activation_word)}]" in normalized(text):
            return True

        return False

    def __remove_activation_word_and_normalize(self, activation_word, text):
        to_remove = f"[{activation_word}]"
        text = text.replace(to_remove, "").strip()
        text = re.sub(f"^{activation_word}", "", text, flags=re.IGNORECASE)
        return text
