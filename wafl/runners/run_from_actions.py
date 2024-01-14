import asyncio

import yaml

from wafl.answerer.entailer import Entailer
from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.logger.local_file_logger import LocalFileLogger

_logger = LocalFileLogger()

COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_END = "\033[0m"


def get_action_list_and_expeted_list_from_yaml(filename, action_name):
    actions = yaml.safe_load(open("actions.yaml"))
    if action_name not in actions:
        raise ValueError(f"Action {action_name} not found in actions.yaml")

    actions_list = [item["action"] for item in actions[action_name]]
    expected_list = [item["expected"] for item in actions[action_name]]
    return actions_list, expected_list


def predict_action(config, actions_list, expected_list):
    interface = DummyInterface(to_utter=actions_list.copy(), print_utterances=True)
    conversation_events = ConversationEvents(
        config=config,
        interface=interface,
        logger=_logger,
    )
    entailer = Entailer(config)
    for expected in expected_list:
        asyncio.run(conversation_events.process_next())
        last_utterance = interface.get_utterances_list()[-1]

        if not last_utterance:
            raise ValueError("The agent did not say anything.")

        if expected and not asyncio.run(
            entailer.left_entails_right(
                last_utterance,
                expected,
                "\n".join(interface.get_utterances_list()[:-1]),
            )
        ):
            del entailer, conversation_events, interface
            raise ValueError(
                f"The utterance '{last_utterance}' does not entail '{expected}'."
            )


def run_action(action_name):
    print(COLOR_GREEN + f"Running the action {action_name}\n" + COLOR_END)
    actions_list, expected_list = get_action_list_and_expeted_list_from_yaml(
        "actions.yaml", action_name
    )
    config = Configuration.load_local_config()
    num_retries = 10
    success = False
    for _ in range(num_retries):
        try:
            predict_action(config, actions_list, expected_list)
            success = True
            break

        except (ValueError, SyntaxError) as e:
            print(COLOR_YELLOW + str(e) + COLOR_END)
            print(COLOR_GREEN + f"Retrying the action {action_name}..." + COLOR_END)

    if success:
        print(COLOR_GREEN + f"Action {action_name} finished." + COLOR_END)

    else:
        print(COLOR_YELLOW + f"Action {action_name} failed." + COLOR_END)


if __name__ == "__main__":
    run_action("action_1_summarise_guardian")
