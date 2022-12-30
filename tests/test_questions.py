from unittest import TestCase

from wafl.events.conversation_events import ConversationEvents
from wafl.events.narrator import Narrator
from wafl.events.utils import is_question
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.qa.qa import QA
from wafl.qa.dataclasses import Query

_wafl_example = """
The user greets
  SAY Hello there!
  username = Are you fine?
  SAY I am glad you are fine!

"""


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

        qa = QA(Narrator(DummyInterface))
        answer = qa.ask(query, user_answer)

        assert answer.is_true()

    def test_yes_or_no_questions_only_accept_positive_or_negative_replies(self):
        interface = DummyInterface(["Hello", "Blue sky", "yes"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_example),
            interface=interface,
        )
        conversation_events.process_next()
        expected = "bot: I am glad you are fine!"
        assert interface.get_utterances_list()[-1] == expected
