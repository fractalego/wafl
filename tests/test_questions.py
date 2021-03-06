from unittest import TestCase

from wafl.conversation.utils import is_question
from wafl.qa.qa import QA
from wafl.qa.dataclasses import Query


class TestQuestions(TestCase):
    def test_are_question(self):
        utterance = "Are you interested in this platter of fish"
        assert is_question(utterance)

    def test_am_question(self):
        utterance = "Am I interested in this platter of fish"
        assert is_question(utterance)

    def test_yes_qa(self):
        query = Query(text="Is the user satisfied with this", is_question=True)
        user_answer = (
            "When asked 'is the user satisfied with this', the user says: 'yes I am.'"
        )

        qa = QA()
        answer = qa.ask(query, user_answer)

        assert answer.text == "yes"
