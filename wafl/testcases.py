from wafl.exceptions import CloseConversation

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface

from wafl.parsing.testcase_parser import get_user_and_bot_lines_from_text
from wafl.qa.entailer import Entailer


class ConversationTestCases:
    def __init__(self, text, knowledge, logger=None):
        self._testcase_data = get_user_and_bot_lines_from_text(text)
        self._knowledge = knowledge
        self._entailer = Entailer(logger)

    def test_single_case(self, name):
        if name not in self._testcase_data:
            raise RuntimeWarning(f"The testcase '{name}' does not exist")

        user_lines = self._testcase_data[name]["user_lines"]
        test_lines = self._testcase_data[name]["lines"]
        is_negated = self._testcase_data[name]["negated"]
        interface = DummyInterface(user_lines)
        conversation = Conversation(self._knowledge, interface=interface, code_path="/")

        print(f"\nRunning test '{name}'.")

        continue_conversations = True
        while continue_conversations:
            try:
                continue_conversations = conversation.input()

            except (IndexError, CloseConversation):
                break

        is_consistent = True
        generated_lines = interface.get_utterances_list()
        for test_line, generated_line in zip(test_lines, generated_lines):
            if not self._lhs_entails_rhs(generated_line, test_line):
                print(f" [test_line] {test_line}")
                print(f" [predicted_line] {generated_line}")
                is_consistent = False
                break

        if (is_consistent and not is_negated) or (not is_consistent and is_negated):
            print(" [Success]")
            return True

        print(" [Fail]")
        print("\n This is how the dialogue went:")
        for line in interface.get_utterances_list():
            print(" " + line)

        return False

    def run(self):
        to_return = True

        for name in self._testcase_data:
            result = self.test_single_case(name)
            if not result:
                to_return = False

        return to_return

    def _lhs_entails_rhs(self, lhs, rhs):
        lhs_name = lhs.split(":")[0]
        rhs_name = rhs.split(":")[0]
        if lhs_name != rhs_name:
            return False

        lhs = ":".join(item.strip() for item in lhs.split(":")[1:])
        rhs = ":".join(item.strip() for item in rhs.split(":")[1:])
        return self._entailer.entails(lhs, rhs) == "True"
