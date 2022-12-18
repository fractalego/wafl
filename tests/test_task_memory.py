from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.conversation.task_memory import TaskMemory
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.logger.local_file_logger import LocalFileLogger

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
    def test__task_memory_class(self):
        task_memory = TaskMemory()
        task_memory.add_question("What is the color of Bob's dress")
        task_memory.add_answer("Red")
        task_memory.add_question("Who is talking")
        prediction = task_memory.get_discussion().strip()
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
            Knowledge(wafl_example),
            interface=interface,
            code_path="functions",
            logger=LocalFileLogger(),
        )
        conversation.input()
        expected = "bot: Hello, bob!"
        assert interface.get_utterances_list()[-1] == expected

    def test__hello_does_not_get_into_task_memory(self):
        interface = DummyInterface(to_utter=["hello", "Albert"])
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "bot: Hello, albert!"
        assert interface.get_utterances_list()[-1] == expected

    def test__task_memory_does_not_propagate_down_for_depth2(self):
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
        expected = "bot: Bananas has been added to the list"
        assert interface.get_utterances_list()[-3] == expected

    def test__task_memory_does_not_propagate_down_for_depth3(self):
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
        expected = "bot: Bananas has been added to the list"
        assert interface.get_utterances_list()[-3] == expected

    def test__task_memory_works_for_yes_questions(self):
        interface = DummyInterface(
            to_utter=[
                "Add apples to the shopping list",
                "yes bananas",
                "no",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example),
            interface=interface,
            code_path="functions",
            logger=LocalFileLogger(),
        )
        conversation.input()
        expected = "bot: Bananas has been added to the list"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-3] == expected

    def test__prior_list_name_is_remembered(self):
        interface = DummyInterface(
            to_utter=[
                "Add apples to the shopping list",
                "add bananas as well",
            ]
        )
        conversation = Conversation(
            Knowledge(memory_example),
            interface=interface,
            code_path="functions",
            logger=LocalFileLogger(),
        )
        conversation.input()
        conversation.input()
        expected = "bot: Bananas has been added to the list"
        assert interface.get_utterances_list()[-1] == expected

    def test__prior_list_name_is_remembered_second_time(self):
        interface = DummyInterface(
            to_utter=[
                "Add tangerines to the shopping list",
                "add bananas as well",
                "ok now add apples",
            ]
        )
        conversation = Conversation(
            Knowledge(memory_example),
            interface=interface,
            code_path="functions",
            logger=LocalFileLogger(),
        )
        conversation.input()
        conversation.input()
        conversation.input()
        expected = "bot: Apples has been added to the list"
        assert interface.get_utterances_list()[-1] == expected