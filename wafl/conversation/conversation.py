from wafl.conversation.utils import is_question
from wafl.inference import BackwardInference
from wafl.qa.qa import Query


class Conversation:
    def __init__(self, knowledge: "BaseKnowledge", interface: "BaseInterface"):
        self._knowledge = knowledge
        self._interface = interface
        self._inference = BackwardInference(self._knowledge, interface)

    def output(self, text: str):
        self._interface.output(text)

    def input(self, text: str):
        if not is_question(text):
            text = f"The user says: {text}"

        query = Query(text=text, is_question=is_question(text), variable="name")
        answer = self._inference.compute(query)

        if not query.is_question and answer.text == "False":
            self._knowledge.add(text)

        return answer
