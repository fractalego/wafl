from wafl.answerer.base_answerer import BaseAnswerer
from wafl.answerer.dialogue_answerer import DialogueAnswerer
from wafl.answerer.inference_answerer import InferenceAnswerer
from wafl.connectors.gptj_prompt_predictor_connector import GPTJPromptPredictorConnector
from wafl.events.narrator import Narrator
from wafl.extractors.entailer import Entailer
from wafl.extractors.task_extractor import TaskExtractor
from wafl.inference.backward_inference import BackwardInference
from wafl.inference.utils import answer_is_informative
from wafl.extractors.dataclasses import Answer, Query


class ArbiterAnswerer(BaseAnswerer):
    def __init__(self, answerers_dict, knowledge, interface, logger):
        self._answerers_dict = answerers_dict
        self._narrator = Narrator(interface)
        self._logger = logger
        self._gptj_connector = GPTJPromptPredictorConnector()
        self._entailer = Entailer(logger)
        self._knowledge = knowledge
        self._task_extractor = TaskExtractor(interface)

    async def answer(self, query_text, policy):
        if await self._knowledge.ask_for_rule_backward(
            Query.create_from_text(f"The user says: {query_text}"), knowledge_name="/"
        ):
            return Answer(text="unknown")

        if await self._knowledge.ask_for_rule_backward(
            Query.create_from_text(
                (await self._task_extractor.extract(query_text)).text
            ),
            knowledge_name="/",
        ):
            return Answer(text="unknown")

        keys_and_scores = []
        for key in self._answerers_dict.keys():
            score = await self._entailer.entails(
                f"The user says: {query_text}",
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
        narrator = Narrator(interface)
        return ArbiterAnswerer(
            {
                "The user asks to do something": InferenceAnswerer(
                    interface,
                    BackwardInference(
                        knowledge, interface, narrator, code_path, logger=logger
                    ),
                    logger,
                ),
                "The user asks for some information about something": DialogueAnswerer(
                    knowledge, interface, logger
                ),
                "The user chats": DialogueAnswerer(knowledge, interface, logger),
            },
            knowledge,
            interface,
            logger,
        )
