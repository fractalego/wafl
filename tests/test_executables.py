from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

wafl_example = """
the user wants to register to the newsletter
  email = what is the user's email
  REMEMBER the user's email is {email}
  newsletter_name = dummy_add_email(email)
  dummy_log_email(email)
  SAY {email} has been added to the newsletter '{newsletter_name}'
"""


class TestExecutables(TestCase):
    def test_executables(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        input_from_user = "Can I register to the newsletter?".capitalize()
        conversation.add(input_from_user)
        expected = "Test@example.com has been added to the newsletter 'fake_newsletter'"
        print(interface.utterances)
        assert interface.utterances[-1] == expected
