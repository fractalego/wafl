import asyncio

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

wafl_example = """
Speed is space over time


the user wants to register to the newsletter
  email = what is the user's email
  REMEMBER the user's email is {email}
  newsletter_name = dummy_add_email(email)
  dummy_log_email(email)
  SAY {email} has been added to the newsletter '{newsletter_name}'
  
item = what does the user want to add to the shopping list?
  shopping_list.append(item)
  SAY {item} has been added to the list
    
item = what does the user want to remove from the shopping list?
  shopping_list.remove(item)
  SAY {item} has been removed from the list

item = what does the user want to add to the test list?
  ! equal(item, "batteries") 
  REMEMBER the user wants to add {item} 
  shopping_list.append(item)
  SAY {item} has been added to the list

item = what does the user want to add to the test list?
  equal(item, "batteries") 
  REMEMBER the user wants to add {item} 
  SAY {item} cannot be added to the list

the user wants to know what is in the shopping list
  items = get_shopping_list_in_english()
  SAY The shopping list contains: {items}
  
the user asks for the time
  time = get_time()
  SAY the time is {time}
    
    
sentence = What does the user want to say
  say_text(sentence)
  

the user says "please define speed":
    testing_fact_from_python_space()
    SAY Test complete
    
"""


class TestExecutables(TestCase):
    def test_executables(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        input_from_user = "Can I register to the newsletter?".capitalize()
        asyncio.run(conversation_events._process_query(input_from_user))
        expected = (
            "bot: Test@example.com has been added to the newsletter 'fake_newsletter'"
        )
        assert interface.get_utterances_list()[-1] == expected

    def test_add_to_list(self):
        interface = DummyInterface(to_utter=["Please add apples to the shopping list"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Apples has been added to the list"
        assert interface.get_utterances_list()[-1] == expected

    def test_remove_from_list(self):
        interface = DummyInterface(
            to_utter=[
                "Please add apples to the shopping list",
                "Please delete apples from the shopping list",
            ]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "bot: Apples has been removed from the list"
        assert interface.get_utterances_list()[-1] == expected

    def test_list_the_items(self):
        interface = DummyInterface(
            to_utter=[
                "Please add apples to the shopping list",
                "Please add bananas to the shopping list",
                "What's in the shopping list",
            ]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "bot: The shopping list contains: apples, bananas"
        expected2 = "bot: The shopping list contains: bananas, apples"
        print(interface.get_utterances_list())
        assert (
            interface.get_utterances_list()[-1] == expected
            or interface.get_utterances_list()[-1] == expected2
        )

    def test_list_the_items2(self):
        interface = DummyInterface(
            to_utter=[
                "Please add apples to the shopping list",
                "Please add bananas to the shopping list",
                "What does the shopping list contain",
            ]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "bot: The shopping list contains: apples, bananas"
        expected2 = "bot: The shopping list contains: bananas, apples"
        assert (
            interface.get_utterances_list()[-1] == expected
            or interface.get_utterances_list()[-1] == expected2
        )

    def test_mispelled_items_are_added_to_the_shopping_list(self):
        interface = DummyInterface(to_utter=["add app list the shopping list"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Add app list the shopping list has been added to the list"
        assert interface.get_utterances_list()[-1] == expected

    def test_question_activates_inference(self):
        interface = DummyInterface(to_utter=["What time is it?"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "The time is"
        assert expected in interface.get_utterances_list()[-1]

    def test_negation(self):
        interface = DummyInterface(to_utter=["add batteries to the test list"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Batteries cannot be added to the list"
        assert interface.get_utterances_list()[-1] == expected

    def test_say_command_in_functions(self):
        interface = DummyInterface(to_utter=["I want to say 'this is a test'"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: This is a test."
        assert interface.get_utterances_list()[-1].lower() == expected.lower()

    def test__facts_work_in_python_space(self):
        interface = DummyInterface(to_utter=["Please define speed"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Test complete"
        assert interface.get_utterances_list()[-1].lower() == expected.lower()
