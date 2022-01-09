from wafl.inference.utils import normalized

from wafl.config import Configuration
from wafl.conversation.utils import is_question, get_answer_using_text, input_is_valid
from wafl.exceptions import InterruptTask
from wafl.inference.backward_inference import BackwardInference


class Conversation:
    def __init__(
        self,
        knowledge: "BaseKnowledge",
        interface: "BaseInterface",
        code_path=None,
        config=None,
    ):
        self._knowledge = knowledge
        self._interface = interface
        self._inference = BackwardInference(self._knowledge, interface, code_path)
        if not config:
            self._config = Configuration.load_local_config()
        else:
            self._config = config

    def output(self, text: str):
        self._interface.output(text)

    def add(self, text: str):
        if not input_is_valid(text):
            return False

        text_is_question = is_question(text)

        try:
            answer = get_answer_using_text(self._inference, self._interface, text)

        except InterruptTask:
            self._interface.output("Task interrupted")
            return

        if (
            self._config.get_value("accept_random_facts")
            and not text_is_question
            and answer.text == "False"
            and not self._interface.bot_has_spoken()
        ):
            self._knowledge.add(text)
            self.output("I will remember it.")

        if not self._interface.bot_has_spoken():
            if not text_is_question and normalized(answer.text) in ["unknown"]:
                self.output(answer.text)

            if text_is_question and answer.text not in ["True", "False"]:
                self.output(answer.text)

            if text_is_question and answer.text == "False":
                self.output("Unknown")

        return answer

    def input(self, activation_word: str = "") -> bool:
        text = self._interface.input()
        if self.__activation_word_in_text(activation_word, text):
            self._interface.check_understanding(True)
            text = self.__remove_activation_word(activation_word, text)
            self.add(text)
            return True

        return False

    def __activation_word_in_text(self, activation_word, text):
        if normalized(activation_word) in normalized(text):
            return True

        return False

    def __remove_activation_word(self, activation_word, text):
        activation_pos = normalized(text).find(normalized(activation_word))
        if activation_pos != -1:
            return text[activation_pos + len(activation_word) :]

        return ""
