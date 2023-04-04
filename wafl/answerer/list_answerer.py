from wafl.answerer.base_answerer import BaseAnswerer
from wafl.events.narrator import Narrator
from wafl.inference.utils import answer_is_informative
from wafl.extractors.dataclasses import Answer


class ListAnswerer(BaseAnswerer):
    def __init__(self, answerers_list, interface, logger):
        self._answerers_list = answerers_list
        self._narrator = Narrator(interface)
        self._logger = logger

    async def answer(self, query_text, policy):
        all_answers = []
        for answerer in self._answerers_list:
            answer = await answerer.answer(query_text, policy)
            all_answers.append(answer)
            if answer_is_informative(answer):
                return answer

        return Answer(text="Unknown")
