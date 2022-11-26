from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.conversation.task_memory import TaskMemory
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

wafl_example = """

The user says hello
  name = What is the user's name
  SAY Hello, {name}!  
  
item = what does the user want to add to the shopping list?
  reset_shopping_list()
  shopping_list.append(item)
  SAY {item} has been added to the list
  ! _ask_another_item

_ask_another_item
  does the user want to add another item
  item = what do you want to add to the shopping list
  SAY {item} has been added to the list
  _ask_another_item

"""

memory_example = """

The user says hello
  name = What is the user's name
  SAY Hello, {name}!  

item = what does the user want to add to the shopping list?
  reset_shopping_list()
  shopping_list.append(item)
  SAY {item} has been added to the list

the user wants to add something
    item = what does the user want to add?
    list_name = which list does the user want to add things to?
    add {item} to {list_name}

"""


class TestWorkingMemory(TestCase):
    def test__working_memory_class(self):
        working_memory = TaskMemory()
        working_memory.add_question("What is the color of Bob's dress")
        working_memory.add_answer("Red")
        working_memory.add_question("Who is talking")
        prediction = working_memory.get_discussion().strip()
        expected = """
Q: What is the color of Bob's dress
A: Red
Q: Who is talking
A: 
        """.strip()
        assert prediction == expected

    def test__executables(self):
        interface = DummyInterface(
            to_utter=[
                "Hello, my name is Bob",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "Hello, bob!"
        assert interface.utterances[0] == expected

    def test__hello_does_not_get_into_working_memory(self):
        interface = DummyInterface(to_utter=["hello", "Albert"])
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "Hello, albert!"
        assert interface.utterances[-1] == expected

    def test__working_memory_does_not_propagate_down_for_depth2(self):
        interface = DummyInterface(
            to_utter=[
                "Add apples to the shopping list",
                "yes",
                "bananas",
                "no",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "Bananas has been added to the list"
        assert interface.utterances[-2] == expected

    def test__working_memory_does_not_propagate_down_for_depth3(self):
        interface = DummyInterface(
            to_utter=[
                "Add apples to the shopping list",
                "yes",
                "pineapple",
                "yes",
                "bananas",
                "no",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "Bananas has been added to the list"
        assert interface.utterances[-2] == expected

    def test__working_memory_works_for_yes_questions(self):
        interface = DummyInterface(
            to_utter=[
                "Add apples to the shopping list",
                "yes bananas",
                "no",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "Bananas has been added to the list"
        assert interface.utterances[-2] == expected

    def test__prior_list_name_is_remembered(self):
        interface = DummyInterface(
            to_utter=[
                "Add apples to the shopping list",
                "yes bananas",
                "add apples as well",
                "what is in the shopping list?"
            ]
        )
        conversation = Conversation(
            Knowledge(memory_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "The shopping list contains: bananas, apples"
        print(interface.utterances)
        assert interface.utterances[-1] == expected