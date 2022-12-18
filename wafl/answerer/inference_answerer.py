from wafl.answerer.base_answerer import BaseAnswerer
from wafl.conversation.narrator import Narrator
from wafl.conversation.task_memory import TaskMemory
from wafl.conversation.utils import is_question
from wafl.qa.dataclasses import Query
from wafl.qa.qa import QA


class InferenceAnswerer(BaseAnswerer):
    def __init__(self, interface, inference, logger):
        self._qa = QA(logger)
        self._logger = logger
        self._narrator = Narrator(interface)
        self._interface = interface
        self._inference = inference

    def answer(self, query_text):
        text = self._narrator.summarize_dialogue()
        if self._logger:
            self._logger.write(
                f"InferenceAnswerer: The context is {text}", self._logger.level.INFO
            )
            self._logger.write(
                f"InferenceAnswerer: The query is {query_text}", self._logger.level.INFO
            )

        return get_answer_using_text(self._inference, self._interface, query_text, text)


def get_answer_using_text(inference, interface, text, prior_conversation):
    working_memory = TaskMemory()
    working_memory.add_story(prior_conversation)
    text = text.capitalize()
    if not is_question(text):
        query_text = f"The user says: '{text}.'"
        working_memory.add_story(query_text)

    else:
        query_text = text

    query = Query(text=query_text, is_question=is_question(text), variable="name")
    interface.bot_has_spoken(False)
    answer = inference.compute(query, working_memory)

    if query.is_question and answer.is_false():
        query = Query(
            text=f"The user asks: '{text}.'",
            is_question=is_question(text),
            variable="name",
        )
        working_memory = TaskMemory()
        working_memory.add_story(query.text)
        interface.bot_has_spoken(False)
        answer = inference.compute(query, working_memory)

    return answer
