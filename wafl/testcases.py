from wafl.exceptions import CloseConversation

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface

from wafl.parsing.testcase_parser import get_user_and_bot_lines_from_text


class ConversationTestCases:
    def __init__(self, text, knowledge):
        self._testcase_data = get_user_and_bot_lines_from_text(text)
        self._knowledge = knowledge

    def test_single_case(self, name):
        if name not in self._testcase_data:
            raise RuntimeWarning(f"The testcase '{name}' does not exist")

        user_lines = self._testcase_data[name]["user_lines"]
        bot_lines = self._testcase_data[name]["bot_lines"]
        is_negated = self._testcase_data[name]["negated"]
        interface = DummyInterface(user_lines)
        conversation = Conversation(
            self._knowledge, interface=interface, code_path="functions"
        )

        print(f"Running test '{name}'...", end="")

        while True:
            try:
                conversation.input()

            except (IndexError, CloseConversation):
                break

        if (bot_lines == interface.utterances and not is_negated) or (
            bot_lines != interface.utterances and is_negated
        ):
            print(" [Success]")
            return True

        print(" [Fail]")
        print("This is how the dialogue went:")
        print(interface.get_dialogue())
        return False

    def run(self):
        to_return = True

        for name in self._testcase_data:
            result = self.test_single_case(name)
            if not result:
                to_return = False

        return to_return
