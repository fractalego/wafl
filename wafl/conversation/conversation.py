from wafl.conversation.utils import is_question
from wafl.inference import BackwardInference
from wafl.qa.qa import Query


class Conversation:
    def __init__(
            self, knowledge: "BaseKnowledge", interface: "BaseInterface", code_path=None
    ):
        self._knowledge = knowledge
        self._interface = interface
        self._inference = BackwardInference(self._knowledge, interface, code_path)

    def output(self, text: str):
        self._interface.output(text)

    def add(self, text: str):
        if not is_question(text):
            query_text = f"The user says: {text}"

        else:
            query_text = text

        query = Query(text=query_text, is_question=is_question(text), variable="name")
        answer = self._inference.compute(query)

        if not query.is_question and answer.text == "False":
            self._knowledge.add(text)

        if query.is_question and answer.text not in ["True", "False"]:
            self.output(answer.text)

        if query.is_question and answer.text == "False":
            self.output("Unknown")

        return answer

    def input(self):
        user_input = self._interface.input()
        self.add(user_input)
