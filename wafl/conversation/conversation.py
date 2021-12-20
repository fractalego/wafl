from wafl.conversation.utils import is_question
from wafl.inference import BackwardInference
from wafl.qa.qa import Query


class Conversation:
    def __init__(self, knowledge, interface):
        self._knowledge = knowledge
        self._interface = interface
        self._inference = BackwardInference(knowledge, interface)

    def output(self, text):
        self._interface.output(text)

    def input(self, text):
        query = Query(text=text, is_question=is_question(text), variable="name")
        self._inference.compute(query)
