from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.parsing.testcase_parser import get_user_and_bot_lines_from_text
from wafl.testcases import ConversationTestCases

_wafl_greetings = """

The user greets
  SAY Hello there!
  username = What is the user's name
  REMEMBER the user is called {username}
  REMEMBER the user's name is {username}
  SAY Nice to meet you, {username}!

""".strip()

_test_case_greetings = """

test the greetings work
  user> Hello
  bot> Hello there!
  bot> What is your name
  user> Bob
  bot> Nice to meet you, bob!

""".strip()


class TestConversationalTestCases(TestCase):
    def test_that_test_case_is_parsed_correctly_with_user_and_bot_present(self):
        dialogue_data = get_user_and_bot_lines_from_text(_test_case_greetings)
        assert list(dialogue_data["test the greetings work"].keys()) == [
            "bot_lines",
            "user_lines",
        ]

    def test_that_test_case_is_parsed_correctly_with_correct_dialogues(self):
        dialogue_data = get_user_and_bot_lines_from_text(_test_case_greetings)
        predicted_for_user = ["Hello", "Bob"]
        predicted_for_bot = [
            "Hello there!",
            "What is your name",
            "Nice to meet you, bob!",
        ]
        assert (
            dialogue_data["test the greetings work"]["user_lines"] == predicted_for_user
        )
        assert (
            dialogue_data["test the greetings work"]["bot_lines"] == predicted_for_bot
        )

    def test_greeting_goes_as_planned(self):
        dialogue_data = get_user_and_bot_lines_from_text(_test_case_greetings)
        interface = DummyInterface(
            dialogue_data["test the greetings work"]["user_lines"]
        )
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        conversation.input()
        assert (
            interface.utterances
            == dialogue_data["test the greetings work"]["bot_lines"]
        )

    def test_conversation_testcase_single_test_success(self):
        testcase = ConversationTestCases(
            _test_case_greetings, Knowledge(_wafl_greetings)
        )
        assert testcase.test_single_case("test the greetings work")

    def test_conversation_testcase_single_test_failure(self):
        new_test_case = _test_case_greetings.replace("Bob", "Albert")
        testcase = ConversationTestCases(new_test_case, Knowledge(_wafl_greetings))
        assert not testcase.test_single_case("test the greetings work")

    def test_conversation_testcase_run_all(self):
        testcase = ConversationTestCases(
            _test_case_greetings, Knowledge(_wafl_greetings)
        )
        assert testcase.run()
