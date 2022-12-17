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
    def __init__(self, narrator, logger=None):
        self._entailer = Entailer(logger)
        self._qa = ConvQA("fractalego/conversation-qa")
        self._narrator = narrator
        self._entailer_to_qa_mapping = {
            "True": "Yes",
            "False": "No",
            "Unknown": "Unknown",
        }

    def ask(self, query: "Query", text: str, task_memory=None):
        query_text = query.text.strip()
        if query.is_question and not is_yes_no_question(query_text):
            answer = self._answer_question(
                query_text, query.variable, text, task_memory
            )
            return answer

        if query.is_question and is_yes_no_question(query_text):
            query_text = get_sentence_from_yn_question(query_text)
            if "the user says: 'yes" in text.lower():
                return Answer(text="Yes")

            return self._check_fact(text, query_text, threshold=0.5)

        return self._check_fact(query_text, text, threshold=0.5)

    def _answer_question(self, query_text, variable_name, text: str, task_memory):
        if query_text[-1] != "?":
            query_text += "?"

        dialogue = Dialogue()

        answer = self._get_answer_by_iterating_over_prior_events_in_the_story(
            text, dialogue.get_text(), query_text, task_memory
        )
        if answer and answer[-1] in [".", ",", "!"]:
            answer = answer[:-1]

        return Answer(text=answer, variable=variable_name)

    def _check_fact(self, query_text, text, threshold):
        if not is_question(text):
            query_context = self._narrator.get_relevant_fact_context(text, query_text)
            answer = self._entailer.entails(query_context, text, threshold=threshold)
            return Answer(text=self._entailer_to_qa_mapping[answer])

        dialogue = Dialogue()
        answer = normalized(self._qa.get_answer(query_text, dialogue.get_text(), text))
        if answer != "unknown" and answer != "no":
            return Answer(text="Yes")

        return Answer(text="No")

    def _get_answer_by_iterating_over_prior_events_in_the_story(
        self, text, dialogue_text, query_text, task_memory
    ):
        for event in text.split(". ")[::-1]:
            event = event.strip()
            if not event or len(event) < 2:
                continue

            answer = normalized(self._qa.get_answer(event, dialogue_text, query_text))
            if task_memory and task_memory.text_is_in_prior_answers(answer):
                continue

            answer_context = self._narrator.get_relevant_query_answer_context(
                text, query_text, answer
            )
            has_entailment = self._entailer.entails(
                event.replace(".'.", "").replace(".'", ""),
                answer_context,
                threshold=0.75,
            )
            if answer != "unknown" and has_entailment == "True":
                return answer

            if "when asked" not in event.lower():
                continue

            has_entailment = self._entailer.entails(
                answer_context,
                event.replace(".'.", "").replace(".'", ""),
                threshold=0.55,
            )
            if answer != "unknown" and has_entailment == "True":
                return answer

        return "unknown"
