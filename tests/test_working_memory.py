from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.conversation.working_memory import WorkingMemory
from wafl.interface.interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

wafl_example = """

The user says hello
  name = What is the user's name
  SAY Hello, {name}!  
  
item = what does the user want to add to the shopping list?
  shopping_list.append(item)
  SAY {item} has been added to the list
  ! the bot asks to add another item to the shopping list

the bot asks to add another item to the shopping list
  does the user want to add another item
  item = what do you want to add to the shopping list
  SAY {item} has been added to the list
  ! the bot asks to add another item to the shopping list

"""


class TestWorkingMemory(TestCase):
    def test_working_memory_class(self):
        working_memory = WorkingMemory()
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

    def test_executables(self):
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

    def ntest_working_memory_does_not_propagate_down(self):

        ### MAKE WORKING MEMORY PROPAGATIONLIMITED TO QUESTIONS, NOT FACTS

        interface = DummyInterface(
            to_utter=[
                "hello"
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "Hello, bob!"
        assert interface.utterances[0] == expected
