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
    list_of_chapters = generate a bullet list of 4 chapters title for a book about a {theme}. Return the result without any number, just a list of titles
    list_of_chapters = get_list_from_text({list_of_chapters}) <create a python list from the bullet list in a text>
    SAY {list_of_chapters}
    chapter_texts = Generate a full paragraph based on this chapter title "{list_of_chapters}". The theme of the paragraph is {theme}. Include the characters "Alberto" and "Maria".
    SAY {chapter_texts}

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
        assert "Alberto" in interface.get_utterances_list()[-1]
        assert "Alberto" in interface.get_utterances_list()[-2]
        assert "Alberto" in interface.get_utterances_list()[-3]
        assert "Alberto" in interface.get_utterances_list()[-4]
        assert "Maria" in interface.get_utterances_list()[-1]
        assert "Maria" in interface.get_utterances_list()[-2]
        assert "Maria" in interface.get_utterances_list()[-3]
        assert "Maria" in interface.get_utterances_list()[-4]
