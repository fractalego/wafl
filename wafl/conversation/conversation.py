import os
import re

from wafl.answerer.arbiter_answerer import ArbiterAnswerer
from wafl.inference.utils import normalized

from wafl.config import Configuration
from wafl.conversation.utils import is_question, input_is_valid
from wafl.exceptions import InterruptTask

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


class Conversation:
    def __init__(
        self,
        knowledge: "BaseKnowledge",
        interface: "BaseInterface",
        code_path=None,
        config=None,
        logger=None,
    ):
        self._answerer = ArbiterAnswerer.create_answerer(
            knowledge, interface, code_path, logger
        )
        self._knowledge = knowledge
        self._interface = interface
        if not config:
            self._config = Configuration.load_local_config()
        else:
            self._config = config

        self._logger = logger
        if logger:
            self._logger.set_depth(0)

    def output(self, text: str):
        self._interface.output(text)

    def add(self, text: str):
        self._interface.bot_has_spoken(False)

        if not input_is_valid(text):
            return False

        text_is_question = is_question(text)

        try:
            answer = self._answerer.answer(text)

        except InterruptTask:
            self._interface.output("Task interrupted")
            return False

        if (
            self._config.get_value("accept_random_facts")
            and not text_is_question
            and not answer.is_true()
            and not self._interface.bot_has_spoken()
        ):
            self._knowledge.add(text)
            self.output("I will remember it.")

        if not self._interface.bot_has_spoken():
            if not text_is_question and normalized(answer.text) in ["unknown"]:
                self.output(answer.text)

            if text_is_question and answer.text not in ["True", "False"]:
                self.output(answer.text)

            if text_is_question and answer.is_false():
                self.output("Unknown")

            if (
                not text_is_question
                and answer.is_false()
                and not self._interface.bot_has_spoken()
            ):
                self._interface.output("negative")

            if (
                not text_is_question
                and answer.is_true()
                and not self._interface.bot_has_spoken()
            ):
                self._interface.output("affermative")

        return answer

    def input(self, activation_word: str = "") -> bool:
        try:
            text = self._interface.input()

        except IndexError:
            return False

        if not self._interface.check_understanding() and self.__activation_word_in_text(
            activation_word, text
        ):
            self._interface.check_understanding(True)
            self._logger.set_depth(0)
            self._logger.write(f"Activation word found {text}")
            if normalized(text) == normalized(activation_word, lower_case=True):
                return True

        text = self.__remove_activation_word_and_normalize(activation_word, text)
        if self._interface.check_understanding():
            answer = self.add(text)
            if answer and answer.text != "False":
                return True

        return False

    def check_understanding(self, do_the_check=None):
        return self._interface.check_understanding(do_the_check)

    def __activation_word_in_text(self, activation_word, text):
        if f"[{normalized(activation_word)}]" in normalized(text):
            return True

        return False

    def __remove_activation_word_and_normalize(self, activation_word, text):
        to_remove = f"[{activation_word}]"
        text = text.replace(to_remove, "").strip()
        text = re.sub(f"^{activation_word}", "", text, flags=re.IGNORECASE)
        return text
