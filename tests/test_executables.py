from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

wafl_example = """

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
"""


class TestExecutables(TestCase):
    def test_executables(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        input_from_user = "Can I register to the newsletter?".capitalize()
        conversation.add(input_from_user)
        expected = (
            "bot: Test@example.com has been added to the newsletter 'fake_newsletter'"
        )
        assert interface.get_utterances_list()[-1] == expected

    def test_add_to_list(self):
        interface = DummyInterface(to_utter=["Please add apples to the shopping list"])
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "bot: Apples has been added to the list"
        assert interface.get_utterances_list()[-1] == expected

    def test_remove_from_list(self):
        interface = DummyInterface(
            to_utter=[
                "Please add apples to the shopping list",
                "Please delete apples from the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        conversation.input()
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
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        conversation.input()
        conversation.input()
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
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        conversation.input()
        conversation.input()
        expected = "bot: The shopping list contains: apples, bananas"
        expected2 = "bot: The shopping list contains: bananas, apples"
        assert (
            interface.get_utterances_list()[-1] == expected
            or interface.get_utterances_list()[-1] == expected2
        )

    def test_mispelled_items_are_added_to_the_shopping_list(self):
        interface = DummyInterface(to_utter=["add app list the shopping list"])
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "bot: Add app list the shopping list has been added to the list"
        assert interface.get_utterances_list()[-1] == expected

    def test_question_activates_inference(self):
        interface = DummyInterface(to_utter=["What time is it?"])
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "The time is"
        assert expected in interface.get_utterances_list()[-1]

    def test_negation(self):
        interface = DummyInterface(to_utter=["add batteries to the test list"])
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "bot: Batteries cannot be added to the list"
        assert interface.get_utterances_list()[-1] == expected

    def test_say_command_in_functions(self):
        interface = DummyInterface(to_utter=["I want to say 'this is a test'"])
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "bot: This is a test."
        assert interface.get_utterances_list()[-1].lower() == expected.lower()
