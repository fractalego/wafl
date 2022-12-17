from wafl.answerer.base_answerer import BaseAnswerer
from wafl.answerer.inference_answerer import InferenceAnswerer
from wafl.answerer.simple_answerer import SimpleAnswerer
from wafl.conversation.narrator import Narrator
from wafl.inference.backward_inference import answer_is_informative, BackwardInference
from wafl.qa.dataclasses import Answer


class ArbiterAnswerer(BaseAnswerer):
    def __init__(self, answerers_list, interface, logger):
        self._answerers_list = answerers_list
        self._narrator = Narrator(interface)
        self._logger = logger

    def answer(self, query_text):
        all_answers = []
        for answerer in self._answerers_list:
            answer = answerer.answer(query_text)
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
            [
                InferenceAnswerer(
                    interface,
                    BackwardInference(
                        knowledge, interface, narrator, code_path, logger=logger
                    ),
                    logger,
                ),
                SimpleAnswerer(narrator, logger),
            ],
            interface,
            logger,
        )
