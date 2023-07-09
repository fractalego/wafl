import random

from wafl.answerer.base_answerer import BaseAnswerer
from wafl.answerer.dialogue_answerer import DialogueAnswerer
from wafl.config import Configuration
from wafl.events.narrator import Narrator
from wafl.extractors.entailer import Entailer
from wafl.extractors.task_extractor import TaskExtractor
from wafl.inference.utils import answer_is_informative
from wafl.extractors.dataclasses import Answer, Query


class ArbiterAnswerer(BaseAnswerer):
    def __init__(self, answerers_dict, knowledge, interface, logger):
        self._answerers_dict = answerers_dict
        self._narrator = Narrator(interface)
        self._interface = interface
        self._logger = logger
        self._entailer = Entailer(logger)
        self._knowledge = knowledge
        self._task_extractor = TaskExtractor(interface)
        self._config = Configuration.load_local_config()

    async def answer(self, query_text, policy):
        task = await self._task_extractor.extract(query_text)
        if await self._knowledge.ask_for_rule_backward(
            Query.create_from_text(task.text),
            knowledge_name="/",
        ):
            return Answer(text="unknown")

        simple_task = f"The user says: {query_text}"
        if await self._knowledge.ask_for_rule_backward(
            Query.create_from_text(simple_task),
            knowledge_name="/",
        ):
            return Answer(text="unknown")

        if (
            not task.is_neutral()
            and self._config.get_value("improvise_tasks")
            and await self._entailer.entails(
                simple_task,
                f"The user gives an order or request",
                return_threshold=True,
                threshold=0.95,
            )
        ):
            await self._interface.output(
                random.choice(
                    [
                        "Let me think",
                        "Uhm",
                        "Thinking about it",
                    ]
                )
            )
            return Answer(text="unknown")

        score = 1
        keys_and_scores = []
        for key in self._answerers_dict.keys():
            if len(self._answerers_dict) > 1:
                score = await self._entailer.entails(
                    simple_task,
                    key,
                    return_threshold=True,
                    threshold=0.5,
                )

            keys_and_scores.append((key, score))

        keys_and_scores = sorted(keys_and_scores, key=lambda x: -x[1])
        all_answers = []
        for key, _ in keys_and_scores:
            answerer = self._answerers_dict[key]
            answer = await answerer.answer(query_text, policy)
            all_answers.append(answer)
            if answer_is_informative(answer) and not answer.is_false():
                return answer

        if any(answer.is_false() for answer in all_answers):
            return Answer(text="False")

        return Answer(text="Unknown")

    @staticmethod
    def create_answerer(knowledge, interface, code_path, logger):
        return ArbiterAnswerer(
            {
                "The user chats": DialogueAnswerer(knowledge, interface, logger),
            },
            knowledge,
            interface,
            logger,
        )
