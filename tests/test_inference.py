from unittest import TestCase

from wafl.inference.backward_inference import BackwardInference
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.qa.dataclasses import Query

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
   house_address = what is {person} house address
   type = what is the tree type at {house_address}

This bot name is Fractalego

the user is very happy

The user's name is Bob

Bob has black hair

Bob's address is 42 Flinch road

42 Flinch road has a peach tree in the garden

""".strip()


class test_Inference(TestCase):
    def test__simple_question(self):
        inference = BackwardInference(Knowledge(wafl_example), DummyInterface())
        query = Query(text="What is this bot's name", is_question=True, variable="name")
        answer = inference.compute(query)
        expected = "Fractalego"
        assert answer.text == expected
        assert answer.variable == query.variable

    def test__fact_check_true(self):
        inference = BackwardInference(Knowledge(wafl_example), DummyInterface())
        query = Query(
            text="The user is in a good mood", is_question=False, variable="name"
        )
        answer = inference.compute(query)
        expected = "True"
        assert answer.text == expected

    def test__fact_check_false(self):
        inference = BackwardInference(Knowledge(wafl_example), DummyInterface())
        query = Query(text="The user is sad", is_question=False, variable="name")
        answer = inference.compute(query)
        expected = "False"
        assert answer.text == expected

    def test__simple_rule(self):
        inference = BackwardInference(Knowledge(wafl_example), DummyInterface())
        query = Query(text="The user says hello!", is_question=False, variable="name")
        answer = inference.compute(query)
        expected = "True"
        assert answer.text == expected

    def test__forward_substitution(self):
        inference = BackwardInference(Knowledge(wafl_example), DummyInterface())
        query = Query(
            text="The user says: I can swim", is_question=False, variable="name"
        )
        answer = inference.compute(query)
        expected = "True"
        assert answer.text == expected

    def test__backward_substitution(self):
        inference = BackwardInference(Knowledge(wafl_example), DummyInterface())
        query = Query(
            text="The user says: I have black hair", is_question=False, variable="name"
        )
        answer = inference.compute(query)
        expected = "True"
        assert answer.text == expected

    def test__forward_substution_2(self):
        inference = BackwardInference(Knowledge(wafl_example), DummyInterface())
        query = Query(
            text="What type of tree is there at Bob's house",
            is_question=True,
            variable="name",
        )
        answer = inference.compute(query)
        expected = "peach tree"
        print(answer)
        assert answer.text == expected
