from wafl.conversation.utils import is_question
from wafl.conversation.working_memory import WorkingMemory
from wafl.inference.backward_inference import BackwardInference
from wafl.qa.qa import Query


class Conversation:
    def __init__(
        self, knowledge: "BaseKnowledge", interface: "BaseInterface", code_path=None
    ):
        self._knowledge = knowledge
        self._interface = interface
        self._inference = BackwardInference(self._knowledge, interface, code_path)

    def output(self, text: str):
        self._interface.output(text)

    def add(self, text: str):
        working_memory = WorkingMemory()

        if not is_question(text):
            query_text = f"The user says: '{text}.'"
            working_memory.add_story(query_text)

        else:
            query_text = text

        query = Query(text=query_text, is_question=is_question(text), variable="name")
        self._interface.bot_has_spoken(False)
        answer = self._inference.compute(query, working_memory)

        if query.is_question and answer.text == "False":
            query = Query(
                text=f"The user asks: '{text}.'",
                is_question=is_question(text),
                variable="name",
            )
            working_memory.add_story(query.text)
            self._interface.bot_has_spoken(False)
            answer = self._inference.compute(query, working_memory)

        if (
            not query.is_question
            and answer.text == "False"
            and not self._interface.bot_has_spoken()
        ):
            ### This needs to be part of the config file
            self._knowledge.add(text)
            self.output("I will remember it.")

        if not self._interface.bot_has_spoken():
            if not query.is_question and answer.text in ["True", "False", "unknown"]:
                self.output(answer.text)

            if query.is_question and answer.text not in ["True", "False"]:
                self.output(answer.text)

            if query.is_question and answer.text == "False":
                self.output("Unknown")

        return answer

    def input(self, activation_word: str = "") -> bool:
        text = self._interface.input()
        if self.__activation_word_in_text(activation_word, text):
            text = self.__remove_activation_word(activation_word, text)
            self.add(text)
            return True

        return False

    def __activation_word_in_text(self, activation_word, text):
        activation_pos = text.lower().find(activation_word.lower())
        if activation_pos == 0 or activation_pos == len(text) - len(activation_word):
            return True

        return False

    def __remove_activation_word(self, activation_word, text):
        activation_pos = text.lower().find(activation_word.lower())
        if activation_pos == 0:
            return text[len(activation_word) :]
        if activation_pos == len(text) - len(activation_word):
            return text[: -len(activation_word)]
