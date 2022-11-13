import logging
import os

from conversation_qa import QA as ConvQA, Dialogue
from wafl.conversation.utils import (
    is_question,
    is_yes_no_question,
    get_sentence_from_yn_question,
)
from wafl.inference.utils import normalized
from wafl.qa.dataclasses import Answer
from wafl.qa.entailer import Entailer

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class QA:
    def __init__(self, logger=None):
        self._entailer = Entailer(logger)
        self._qa = ConvQA("fractalego/conversation-qa")
        self._entailer_to_qa_mapping = {
            "True": "Yes",
            "False": "No",
            "Unknown": "Unknown",
        }

    def ask(self, query: "Query", text: str):
        query_text = query.text.strip()
        if query.is_question and not is_yes_no_question(query_text):
            return self.__answer_question(query_text, query.variable, text)

        if query.is_question and is_yes_no_question(query_text):
            query_text = get_sentence_from_yn_question(query_text)
            if "the user says: 'yes" in text.lower():
                return Answer(text="Yes")

            return self.__check_fact(text, query_text, threshold=0.5)

        return self.__check_fact(query_text, text, threshold=0.5)

    def __answer_question(self, query_text, variable_name, text: str):
        if query_text[-1] != "?":
            query_text += "?"

        dialogue = Dialogue()
        answer = self._qa.get_answer(text, dialogue.get_text(), query_text)
        if answer and answer[-1] in [".", ",", "!"]:
            answer = answer[:-1]

        return Answer(text=answer, variable=variable_name)

    def __check_fact(self, query_text, text, threshold):
        if not is_question(text):
            answer = self._entailer.entails(query_text, text, threshold=threshold)
            return Answer(text=self._entailer_to_qa_mapping[answer])

        dialogue = Dialogue()
        answer = normalized(self._qa.get_answer(query_text, dialogue.get_text(), text))
        if answer != "unknown" and answer != "no":
            return Answer(text="Yes")

        return Answer(text="No")
