import asyncio

import yaml

from wafl.answerer.entailer import Entailer
from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.logger.local_file_logger import LocalFileLogger

_logger = LocalFileLogger()


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
    print(f"Running the action {action_name}\n")
    actions_list, expected_list = get_action_list_and_expeted_list_from_yaml(
        "actions.yaml", action_name
    )
    config = Configuration.load_local_config()
    num_retries = 10
    for _ in range(num_retries):
        try:
            predict_action(config, actions_list, expected_list)
            break

        except (ValueError, SyntaxError) as e:
            print(e)
            print(f"Retrying the action {action_name}...")

    print(f"Action {action_name} finished.")


if __name__ == "__main__":
    run_action("action_1_summarise_guardian")
