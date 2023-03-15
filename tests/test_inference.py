import asyncio
from unittest import TestCase
from wafl.events.narrator import Narrator
from wafl.events.task_memory import TaskMemory
from wafl.inference.backward_inference import BackwardInference
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.extractors.dataclasses import Query
from wafl.logger.local_file_logger import LocalFileLogger

_logger = LocalFileLogger()

wafl_example = """

The user greets
  username = What is the user's name
  SAY hello to you, {username}!

The user says they can swim
  username = What is the user's name
  USER is called {username}
  
color = What is the user's hair color
  username = What is the user's name
  {username} has {color} hair
  
{person} has a {type} tree in the garden
   person = what is the user's name
   house_address = what is {person}'s address
   type = what is the tree type at {house_address}

This bot name is Fractalego

the user is very happy

The user's name is Bob

Bob has black hair

Bob's address is 42 Flinch road

42 Flinch road has a peach tree in the garden

""".strip()


class TestInference(TestCase):
    def test__simple_question(self):
        interface = DummyInterface()
        inference = BackwardInference(
            SingleFileKnowledge(wafl_example), interface, Narrator(interface)
        )
        query = Query(text="What is this bot's name", is_question=True, variable="name")
        answer = asyncio.run(inference.compute(query))
        expected = "fractalego"
        assert answer.text.lower() == expected
        assert answer.variable == query.variable

    def test__fact_check_true(self):
        interface = DummyInterface()
        inference = BackwardInference(
            SingleFileKnowledge(wafl_example), interface, Narrator(interface)
        )
        query = Query(
            text="The user is in a good mood", is_question=False, variable="name"
        )
        answer = asyncio.run(inference.compute(query))
        assert answer.is_true()

    def test__fact_check_false(self):
        interface = DummyInterface()
        inference = BackwardInference(
            SingleFileKnowledge(wafl_example), interface, Narrator(interface)
        )
        query = Query(text="The user is sad", is_question=False, variable="name")
        answer = asyncio.run(inference.compute(query))
        assert answer.is_false()

    def test__simple_rule(self):
        interface = DummyInterface()
        inference = BackwardInference(
            SingleFileKnowledge(wafl_example), interface, Narrator(interface)
        )
        query = Query(text="The user says hello!", is_question=False, variable="name")
        answer = asyncio.run(inference.compute(query))
        assert answer.is_true()

    def test__forward_substitution(self):
        interface = DummyInterface()
        inference = BackwardInference(
            SingleFileKnowledge(wafl_example), interface, Narrator(interface)
        )
        query = Query(
            text="The user says: I can swim", is_question=False, variable="name"
        )
        answer = asyncio.run(inference.compute(query))
        assert answer.is_true()

    def test__backward_substitution(self):
        interface = DummyInterface()
        inference = BackwardInference(
            SingleFileKnowledge(wafl_example), interface, Narrator(interface)
        )
        query = Query(
            text="The user says: I have black hair", is_question=False, variable="name"
        )
        answer = asyncio.run(inference.compute(query))
        assert answer.is_true()

    def test__forward_substution_2(self):
        interface = DummyInterface()
        inference = BackwardInference(
            SingleFileKnowledge(wafl_example),
            interface,
            Narrator(interface),
            logger=_logger,
        )
        query = Query(
            text="What type of tree is there at Bob's house",
            is_question=True,
            variable="name",
        )
        task_memory = TaskMemory()
        answer = asyncio.run(
            inference._look_for_answer_in_rules(query, task_memory, "/", 0, False)
        )
        expected = "peach"
        assert answer.text == expected
