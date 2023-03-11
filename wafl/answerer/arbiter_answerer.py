from wafl.answerer.base_answerer import BaseAnswerer
from wafl.answerer.chitchat_answerer import ChitChatAnswerer
from wafl.answerer.fact_answerer import FactAnswerer
from wafl.answerer.generated_answerer import GeneratedAnswerer
from wafl.answerer.inference_answerer import InferenceAnswerer
from wafl.answerer.list_answerer import ListAnswerer
from wafl.answerer.simple_answerer import SimpleAnswerer
from wafl.connectors.gptj_prompt_predictor_connector import GPTJPromptPredictorConnector
from wafl.events.narrator import Narrator
from wafl.extractors.entailer import Entailer
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

    async def answer(self, query_text):
        if self._knowledge.ask_for_rule_backward(
            Query.create_from_text(f"The user says: {query_text}"), knowledge_name="/"
        ):
            return Answer(text="unknown")

        keys_and_scores = []
        for key in self._answerers_dict.keys():
            score = self._entailer.entails(
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
            answer = await answerer.answer(query_text)
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
                "The user asks for some information about something": ListAnswerer(
                    [
                        FactAnswerer(knowledge, narrator, logger),
                        SimpleAnswerer(narrator, logger),
                        GeneratedAnswerer(narrator, logger),
                    ],
                    interface,
                    logger,
                ),
                "The user chats": ChitChatAnswerer(narrator, logger),
            },
            knowledge,
            interface,
            logger,
        )
