import logging
import os

from conversation_qa import QA as ConvQA, Dialogue
from wafl.conversation.utils import is_question
from wafl.inference.utils import normalized
from wafl.qa.dataclasses import Answer
from wafl.qa.entailer import Entailer

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class QA:
    def __init__(self):
        self._entailer = Entailer()
        self._qa = ConvQA("fractalego/conversation-qa")

    def ask(self, query: "Query", text: str):
        if query.is_question:
            return self.__answer_question(query, text)

        return self.__check_fact(query, text)

    def __answer_question(self, query: "Query", text: str):
        query_text = query.text.strip()
        if query_text[-1] != "?":
            query_text += "?"

        dialogue = Dialogue()
        answer = self._qa.get_answer(text, dialogue.get_text(), query_text)

        return Answer(text=answer, variable=query.variable)

    def __check_fact(self, query, text):
        if not is_question(text):
            answer = self._entailer.entails(query.text, text)
            return Answer(text=str(answer))

        dialogue = Dialogue()
        answer = normalized(self._qa.get_answer(query.text, dialogue.get_text(), text))
        if answer != "unknown" and answer != "no":
            return Answer(text="True")

        return Answer(text="False")
