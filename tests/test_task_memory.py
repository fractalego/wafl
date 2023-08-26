import asyncio

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.events.task_memory import TaskMemory
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.logger.local_file_logger import LocalFileLogger

wafl_example = """

The user says or wants to say hello
  name = What is the user's name
  SAY Hello, {name}!  
  
item = what does the user want to add to the shopping list?
  reset_shopping_list()
  shopping_list.append(item)
  SAY {item} has been added to the list
  ! _ask_another_item

_ask_another_item
  does the user want to add another item
  item = what do you want to add
  SAY {item} has been added to the shopping list
  _ask_another_item

"""

memory_example = """

The user says hello
  name = What is the user's name
  SAY Hello, {name}!  

the user wants to know what is in the shopping list
  SAY the shopping list contains: nothing

item = what does the user want to add to the shopping list?
  reset_shopping_list()
  shopping_list.append(item)
  SAY {item} has been added to the shopping list

the user wants to add something
    item = what does the user want to add?
    list_name = which list does the user want to add things to?
    add {item} to {list_name}

"""


class TestTaskMemory(TestCase):
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
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_example),
            interface=interface,
            code_path="/",
            logger=LocalFileLogger(),
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Hello, bob!"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected

    def test__hello_does_not_get_into_task_memory(self):
        interface = DummyInterface(to_utter=["hello", "Albert"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
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
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Bananas has been added to the shopping list"
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
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Bananas has been added to the shopping list"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-3] == expected

    def test__task_memory_works_for_yes_questions(self):
        interface = DummyInterface(
            to_utter=[
                "Add apples to the shopping list",
                "yes bananas",
                "no",
            ]
        )
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_example),
            interface=interface,
            code_path="/",
            logger=LocalFileLogger(),
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Bananas has been added to the shopping list"
        assert interface.get_utterances_list()[-3] == expected

    def test__prior_list_name_is_remembered(self):
        interface = DummyInterface(
            to_utter=[
                "Add apples to the shopping list",
                "add bananas as well",
            ]
        )
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, memory_example),
            interface=interface,
            code_path="/",
            logger=LocalFileLogger(),
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "bot: Bananas has been added to the shopping list"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected

    def test__prior_list_name_is_remembered_second_time(self):
        interface = DummyInterface(
            to_utter=[
                "add tangerines to the shopping list",
                "add bananas to the shopping list",
                "ok now add apples",
            ]
        )
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, memory_example),
            interface=interface,
            code_path="/",
            logger=LocalFileLogger(),
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        expected = "bot: Apples has been added to the shopping list"
        assert interface.get_utterances_list()[-1] == expected

    def test__prior_list_name_is_remembered_second_time_for_coffee_filters(self):
        interface = DummyInterface(
            to_utter=[
                "What's in the shopping list?",
                "ok add apples.",
                "add coffee filters",
            ]
        )
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, memory_example),
            interface=interface,
            code_path="/",
            logger=LocalFileLogger(),
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "bot: Coffee filters has been added to the shopping list"
        assert interface.get_utterances_list()[-1] == expected
