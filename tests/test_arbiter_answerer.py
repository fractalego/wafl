import asyncio
import os

from unittest import TestCase

from wafl.answerer.arbiter_answerer import ArbiterAnswerer
from wafl.events.answerer_creator import create_answerer
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.policy.answerer_policy import AnswerPolicy

_path = os.path.dirname(__file__)

_wafl_rules = """

This bot name is Computer
This bot is doing well

""".strip()


class TestArbiterAnswerer(TestCase):
    def test_generated_answer(self):
        interface = DummyInterface()
        policy = AnswerPolicy(interface)
        answerer = ArbiterAnswerer.create_answerer(
            knowledge=SingleFileKnowledge(_wafl_rules),
            interface=interface,
            code_path="/",
            logger=None,
        )
        answer = asyncio.run(answerer.answer("What color is the sky?", policy))
        expected = "I believe the sky is blue."
        self.assertEqual(expected, answer.text)

    def test_generated_answer_from_conversation(self):
        interface = DummyInterface()
        policy = AnswerPolicy(interface)
        answerer = create_answerer(
            knowledge=SingleFileKnowledge(_wafl_rules),
            interface=interface,
            code_path="/",
            logger=None,
        )
        answer = asyncio.run(answerer.answer("What color is the sky?", policy))
        expected = "I believe the sky is blue."
        self.assertEqual(expected, answer.text)

    def test_generated_answer_from_conversation2(self):
        interface = DummyInterface(["what is the capital of Italy?"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_rules),
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: I believe it is Rome"
        self.assertEqual(expected, interface.get_utterances_list()[-1])

    def test_generated_answer_from_conversation3(self):
        interface = DummyInterface(
            ["what is the capital of Italy .", "how tall is Micheal Jordan ."]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_rules),
            interface=interface,
        )
        interface.output("Please say computer to activate me.")
        interface.output("What can I do for you?")
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "6'7\""
        self.assertIn(expected, interface.get_utterances_list()[-1])

    def test_fact_answer(self):
        interface = DummyInterface()
        policy = AnswerPolicy(interface)
        answerer = ArbiterAnswerer.create_answerer(
            knowledge=SingleFileKnowledge(_wafl_rules),
            interface=interface,
            code_path="/",
            logger=None,
        )
        answer = asyncio.run(answerer.answer("What is the name of this bot", policy))
        expected = "computer"
        self.assertEqual(expected, answer.text)

    def test_chitchat(self):
        interface = DummyInterface()
        policy = AnswerPolicy(interface)
        answerer = ArbiterAnswerer.create_answerer(
            knowledge=SingleFileKnowledge(_wafl_rules),
            interface=interface,
            code_path="/",
            logger=None,
        )
        answer = asyncio.run(answerer.answer("good good", policy))
        expected = "hi"
        self.assertEqual(expected, answer.text)

    def test__conversation_input_returns_chitchat_for_trivial_input(self):
        interface = DummyInterface(["uhm what"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(""), interface=interface
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: I don't understand"
        self.assertEqual(expected, interface.get_utterances_list()[-1])
