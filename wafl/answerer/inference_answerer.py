from wafl.answerer.base_answerer import BaseAnswerer
from wafl.events.narrator import Narrator
from wafl.events.task_memory import TaskMemory
from wafl.extractors.entailer import Entailer
from wafl.extractors.task_extractor import TaskExtractor
from wafl.simple_text_processing.questions import is_question
from wafl.extractors.dataclasses import Query, Answer
from wafl.extractors.extractor import Extractor


class InferenceAnswerer(BaseAnswerer):
    def __init__(self, config, interface, inference, logger):
        self._qa = Extractor(config, logger)
        self._logger = logger
        self._narrator = Narrator(interface)
        self._interface = interface
        self._inference = inference
        self._task_extractor = TaskExtractor(config, interface)
        self._entailer = Entailer(config, logger)

    async def answer(self, query_text, policy):
        prior_conversation = self._narrator.summarize_dialogue()
        if self._logger:
            self._logger.write(
                f"InferenceAnswerer: The context is {prior_conversation}",
                self._logger.level.INFO,
            )
            self._logger.write(
                f"InferenceAnswerer: The query is {query_text}", self._logger.level.INFO
            )

        simple_task = f"The user says: '{query_text.capitalize()}'"
        task_answer = await self._task_extractor.extract(simple_task)
        if task_answer.is_neutral():
            task = simple_task

        else:
            task = task_answer.text

        task_texts = split_tasks(task)
        answers = []
        for task_text in task_texts:
            result = await self._entailer.entails(
                simple_task, task_text, return_threshold=True, threshold=0.6
            )
            if not result:
                task_text = simple_task

            await self._interface.add_choice(
                f"The bot understands the task to be '{task_text}'"
            )

            answers.append(
                await get_answer_using_text(
                    self._inference,
                    self._interface,
                    task_text,
                    prior_conversation,
                    policy,
                )
            )

        if len(answers) > 1:
            return perform_and(answers)

        if not answers:
            return Answer.create_neutral()

        return answers[0]


def split_tasks(task_text):
    return [item.strip() for item in task_text.split("|") if item]


def perform_and(answers):
    result = all([answer.is_true() for answer in answers])
    if result:
        return Answer.create_true()

    if any([answer.is_neutral() for answer in answers]):
        return Answer.create_neutral()

    return Answer.create_false()


async def get_answer_using_text(
    inference, interface, task_text, prior_conversation, policy
):
    working_memory = TaskMemory()
    working_memory.add_story(prior_conversation)
    working_memory.add_story(task_text)
    query = Query(text=task_text, is_question=is_question(task_text), variable="name")
    interface.bot_has_spoken(False)
    answer = await inference.compute(query, working_memory, policy=policy)
    return answer
