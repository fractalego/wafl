from wafl.answerer.base_answerer import BaseAnswerer
from wafl.events.narrator import Narrator
from wafl.events.task_memory import TaskMemory
from wafl.extractors.entailer import Entailer
from wafl.extractors.task_extractor import TaskExtractor
from wafl.simple_text_processing.questions import is_question
from wafl.extractors.dataclasses import Query
from wafl.extractors.extractor import Extractor


class InferenceAnswerer(BaseAnswerer):
    def __init__(self, interface, inference, logger):
        self._qa = Extractor(logger)
        self._logger = logger
        self._narrator = Narrator(interface)
        self._interface = interface
        self._inference = inference
        self._task_extractor = TaskExtractor(interface)
        self._entailer = Entailer(logger)

    async def answer(self, query_text, policy):
        text = self._narrator.summarize_dialogue()
        if self._logger:
            self._logger.write(
                f"InferenceAnswerer: The context is {text}", self._logger.level.INFO
            )
            self._logger.write(
                f"InferenceAnswerer: The query is {query_text}", self._logger.level.INFO
            )

        return await get_answer_using_text(
            self._inference,
            self._interface,
            self._task_extractor,
            self._entailer,
            query_text,
            text,
            policy,
        )


async def get_answer_using_text(
    inference, interface, task_extractor, entailer, text, prior_conversation, policy
):
    working_memory = TaskMemory()
    working_memory.add_story(prior_conversation)
    text = text.capitalize()
    query_text = f"The user says: '{text}.'"
    working_memory.add_story(query_text)
    query = Query(text=query_text, is_question=is_question(text), variable="name")
    interface.bot_has_spoken(False)
    answer = await inference.compute(query, working_memory, policy=policy)

    if answer.is_neutral():
        task_text = (await task_extractor.extract(text)).text
        print("TASK:", text + " | " + task_text)
        if "not" in task_text:
            return answer

        if entailer.entails(query_text, task_text, return_threshold=True):
            return answer

        query = Query(
            text=task_text,
            is_question=is_question(text),
            variable="name",
        )
        working_memory = TaskMemory()
        working_memory.add_story(query.text)
        interface.bot_has_spoken(False)
        answer = await inference.compute(query, working_memory, policy=policy)

    return answer
