import logging
import os

from wafl.connectors.bridges.llm_qa_bridge import LLMQABridge
from wafl.simple_text_processing.questions import (
    is_question,
    is_yes_no_question,
    get_sentence_from_yn_question,
)
from wafl.simple_text_processing.normalize import normalized
from wafl.extractors.dataclasses import Answer
from wafl.extractors.entailer import Entailer

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class Extractor:
    def __init__(self, config, narrator, logger=None):
        self._entailer = Entailer(config, logger)
        self._qa = LLMQABridge(config)
        self._narrator = narrator
        self._logger = logger
        self._entailer_to_qa_mapping = {
            "True": "Yes",
            "False": "No",
            "Unknown": "Unknown",
        }

    async def extract(self, query: "Query", text: str, task_memory=None):
        if self._logger:
            self._logger.write(f"Extractor: the query is {query}")
            self._logger.write(f"Extractor: the text is {text}")

        query_text = query.text.strip()
        if query.is_question and not is_yes_no_question(query_text):
            answer = await self._answer_question(
                query_text, query.variable, text, task_memory
            )
            return answer

        if query.is_question and is_yes_no_question(query_text):
            query_text = get_sentence_from_yn_question(query_text)
            if "the user says: 'yes" in text.lower():
                return Answer(text="Yes")

            return await self._check_fact(
                text, query_text, query.variable, threshold=0.5
            )

        return await self._check_fact(query_text, text, query.variable, threshold=0.5)

    async def _answer_question(self, query_text, variable_name, text: str, task_memory):
        answer = await self._get_answer(text, "", query_text)
        if answer and answer[-1] in [".", ",", "!"]:
            answer = answer[:-1]

        return Answer(text=answer, variable=variable_name)

    async def _check_fact(self, query_text, text, variable_name, threshold):
        if not is_question(text):
            query_context = self._narrator.get_relevant_fact_context(text, query_text)
            answer = await self._entailer.entails(
                query_context, text, threshold=threshold
            )
            return Answer(
                text=self._entailer_to_qa_mapping[answer], variable=variable_name
            )

        answer_text = normalized(await self._qa.get_answer(query_text, "", text))
        if answer_text != "unknown" and answer_text != "no":
            return Answer(text="Yes", variable=variable_name)

        return Answer(text="No", variable=variable_name)

    async def _get_answer(self, story, dialogue_text, query_text):
        query_text = _clean_query_text(query_text)
        if self._logger:
            self._logger.write(f"Extractor: answering the query {query_text}")

        answer_text = normalized(
            await self._qa.get_answer(story, dialogue_text, query_text)
        )

        if self._logger:
            self._logger.write(f"Extractor: the answer is {answer_text}")

        if not answer_text:
            answer_text = "unknown"

        return answer_text

    def get_entailer(self):
        return self._entailer


def _split_events(text):
    return text.split("; ")


def _clean_events(text):
    text = text.strip()
    text = text.replace(" 's ", "'s ")
    text = text.replace(".'", "'")
    text = text.replace('."', '"')
    if text and text[-1] == ".":
        text = text[:-1]

    return text


def _clean_query_text(text):
    text = text.replace(".'?", "?'")
    text = text.replace("'?", "?'")
    return text
