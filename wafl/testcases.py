from wafl.answerer.entailer import Entailer
from wafl.simple_text_processing.deixis import from_user_to_bot, from_bot_to_user
from wafl.exceptions import CloseConversation
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.parsing.testcase_parser import get_user_and_bot_lines_from_text


class ConversationTestCases:
    BLUE_COLOR_START = "\033[94m"
    RED_COLOR_START = "\033[31m"
    GREEN_COLOR_START = "\033[32m"
    COLOR_END = "\033[0m"

    def __init__(self, config, text, logger=None):
        self._config = config
        self._testcase_data = get_user_and_bot_lines_from_text(text)
        self._entailer = Entailer(config)

    async def test_single_case(self, name):
        if name not in self._testcase_data:
            raise RuntimeWarning(f"The testcase '{name}' does not exist")

        user_lines = self._testcase_data[name]["user_lines"]
        test_lines = self._testcase_data[name]["lines"]
        is_negated = self._testcase_data[name]["negated"]
        interface = DummyInterface(user_lines)
        conversation_events = ConversationEvents(self._config, interface=interface)
        await conversation_events._knowledge._initialize_retrievers()

        print(self.BLUE_COLOR_START + f"\nRunning test '{name}'." + self.COLOR_END)
        continue_conversations = True
        while continue_conversations:
            try:
                continue_conversations = await conversation_events.process_next()

            except (IndexError, CloseConversation):
                break

        is_consistent = True
        generated_lines = interface.get_utterances_list()
        prior_dialogue = []
        for test_line, generated_line in zip(test_lines, generated_lines):
            if not await self._lhs_is_similar_to(
                generated_line, test_line, prior_dialogue
            ):
                print(f" [test_line] {test_line}")
                print(f" [predicted_line] {generated_line}")
                is_consistent = False
                break

            prior_dialogue.append(generated_line)

        if (is_consistent and not is_negated) or (not is_consistent and is_negated):
            print(self.GREEN_COLOR_START + " [Success]\n\n" + self.COLOR_END)
            return True

        print(self.RED_COLOR_START + " [Fail]\n\n" + self.COLOR_END)
        print("\n This is how the dialogue went:")
        for line in interface.get_utterances_list():
            print(" " + line)

        return False

    async def run(self):
        to_return = True
        for name in self._testcase_data:
            result = await self.test_single_case(name)
            if not result:
                to_return = False

        return to_return

    async def _lhs_is_similar_to(self, lhs, rhs, prior_dialogue):
        lhs_name = lhs.split(":")[0].strip()
        rhs_name = rhs.split(":")[0].strip()
        if lhs_name != rhs_name:
            return False

        return await self._entailer.left_entails_right(
            lhs, rhs, "\n".join(prior_dialogue)
        )

    def _apply_deixis(self, line):
        name = line.split(":")[0].strip()

        if name.lower() == "user":
            return from_user_to_bot(line)

        if name.lower() == "bot":
            return from_bot_to_user(line)
