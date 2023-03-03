import asyncio
import os

from unittest import TestCase
from wafl.answerer.arbiter_answerer import ArbiterAnswerer
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)

_wafl_rules = """

This bot name is Computer
This bot is doing well

""".strip()


class TestArbiterAnswerer(TestCase):
    def test_generated_answer(self):
        interface = DummyInterface()
        answerer = ArbiterAnswerer.create_answerer(
            knowledge=SingleFileKnowledge(_wafl_rules),
            interface=interface,
            code_path="/",
            logger=None,
        )
        answer = asyncio.run(answerer.answer("What color is the sky?"))
        expected = "I believe the sky is blue."
        print(answer)
        self.assertEqual(expected, answer.text)

    def test_fact_answer(self):
        interface = DummyInterface()
        answerer = ArbiterAnswerer.create_answerer(
            knowledge=SingleFileKnowledge(_wafl_rules),
            interface=interface,
            code_path="/",
            logger=None,
        )
        answer = asyncio.run(answerer.answer("What is the name of this bot"))
        expected = "computer"
        self.assertEqual(expected, answer.text)

    def test_chitchat(self):
        interface = DummyInterface()
        answerer = ArbiterAnswerer.create_answerer(
            knowledge=SingleFileKnowledge(_wafl_rules),
            interface=interface,
            code_path="/",
            logger=None,
        )
        answer = asyncio.run(answerer.answer("good good"))
        expected = "hi"
        print(answer)
        self.assertEqual(expected, answer.text)
