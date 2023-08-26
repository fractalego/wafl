from wafl.answerer.base_answerer import BaseAnswerer
from wafl.answerer.dialogue_answerer import DialogueAnswerer
from wafl.answerer.inference_answerer import InferenceAnswerer
from wafl.config import Configuration
from wafl.events.narrator import Narrator
from wafl.extractors.entailer import Entailer
from wafl.extractors.task_extractor import TaskExtractor
from wafl.inference.backward_inference import BackwardInference
from wafl.inference.utils import answer_is_informative
from wafl.extractors.dataclasses import Answer, Query


class ArbiterAnswerer(BaseAnswerer):
    def __init__(self, config, answerers_dict, knowledge, interface, logger):
        self._answerers_dict = answerers_dict
        self._narrator = Narrator(interface)
        self._interface = interface
        self._logger = logger
        self._entailer = Entailer(config, logger)
        self._knowledge = knowledge
        self._task_extractor = TaskExtractor(config, interface)
        self._config = Configuration.load_local_config()

    async def answer(self, query_text, policy):
        simple_task = f"The user says: {query_text.capitalize()}"
        task = await self._task_extractor.extract(simple_task)
        if not task.is_neutral() and await self._knowledge.ask_for_rule_backward(
            Query.create_from_text(task.text),
            knowledge_name="/",
        ):
            simple_task += ". There is a rule for that request."

        elif await self._knowledge.ask_for_rule_backward(
            Query.create_from_text(simple_task),
            knowledge_name="/",
        ):
            simple_task += ". There is a rule for that request."

        else:
            simple_task += ". There is no rule for that request."

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
    def create_answerer(config, knowledge, interface, code_path, logger):
        narrator = Narrator(interface)
        return ArbiterAnswerer(
            config,
            {
                "The user greets and there is no rule for that query": DialogueAnswerer(
                    config, knowledge, interface, logger
                ),
                "The user speaks about themselves and there is no rule for that query": DialogueAnswerer(
                    config, knowledge, interface, logger
                ),
                "The user makes small talk and there is no rule for that query": DialogueAnswerer(
                    config, knowledge, interface, logger
                ),
                "The user gives an order or request and there is a rule for that query": InferenceAnswerer(
                    config,
                    interface,
                    BackwardInference(
                        config,
                        knowledge,
                        interface,
                        narrator,
                        code_path,
                        logger=logger,
                        generate_rules=False,
                    ),
                    logger,
                ),
                "The user gives an order or request and there is no rule for that query": InferenceAnswerer(
                    config,
                    interface,
                    BackwardInference(
                        config,
                        knowledge,
                        interface,
                        narrator,
                        code_path,
                        logger=logger,
                        generate_rules=True,
                    ),
                    logger,
                ),
                "The user gives a command and and there is no rule for that query": InferenceAnswerer(
                    config,
                    interface,
                    BackwardInference(
                        config,
                        knowledge,
                        interface,
                        narrator,
                        code_path,
                        logger=logger,
                        generate_rules=True,
                    ),
                    logger,
                ),
            },
            knowledge,
            interface,
            logger,
        )
