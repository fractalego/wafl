import asyncio

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.events.narrator import Narrator
from wafl.simple_text_processing.questions import is_question
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.extractors.extractor import Extractor
from wafl.extractors.dataclasses import Query

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
        config = Configuration.load_local_config()
        qa = Extractor(config, Narrator(DummyInterface))
        answer = asyncio.run(qa.extract(query, user_answer))

        assert answer.is_true()

    def test_yes_or_no_questions_only_accept_positive_or_negative_replies(self):
        interface = DummyInterface(["Hello", "Blue sky", "yes"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, _wafl_example),
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: I am glad you are fine!"
        assert interface.get_utterances_list()[-1] == expected
