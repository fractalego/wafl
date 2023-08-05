import asyncio
import os

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)

_rules = """

the user wants to write a book
    theme = what is the book about?
    list_of_chapters = Generate a bullet list of 4 chapters names for a book. The theme of the book is {theme}.
    SAY [{list_of_chapters}]
    chapter_texts = Generate a full paragraph based on this chapter title "[{list_of_chapters}]". Include the characters "Alberto" and "Maria". Write at least three sentences.
    SAY [{chapter_texts}]

"""


class TestListType(TestCase):
    def test__rule_line_can_return_list(self):
        interface = DummyInterface(
            [
                "I want to write a book",
                "space opera",
            ]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_rules), interface=interface, code_path="/"
        )
        asyncio.run(conversation_events.process_next())
        [print(item) for item in interface.get_utterances_list()]
        assert "alberto" in interface.get_utterances_list()[-1].lower()
        assert "alberto" in interface.get_utterances_list()[-2].lower()
        assert "alberto" in interface.get_utterances_list()[-3].lower()
        assert "alberto" in interface.get_utterances_list()[-4].lower()
        assert "maria" in interface.get_utterances_list()[-1].lower()
        assert "maria" in interface.get_utterances_list()[-2].lower()
        assert "maria" in interface.get_utterances_list()[-3].lower()
        assert "maria" in interface.get_utterances_list()[-4].lower()
