import json

import pandas as pd
from tqdm import tqdm

from create_rules_dataset import generate_conversation
from wafl.config import Configuration
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector
from wafl.retriever.dense_retriever import DenseRetriever


if __name__ == "__main__":
    config = Configuration.load_local_config()
    dataset_items = json.load(open("data/rules_and_conversations.json"))
    discarded_items = json.load(open("data/discarded_rules_and_conversations.json"))
    accepted_items = json.load(open("data/accepted_rules_and_conversations.json"))

    for item in dataset_items:
        if item in discarded_items or item in accepted_items:
            continue

        print(item)
        y_n = input("Do you want to accept this item? (y/n)")
        if y_n != "y":
            discarded_items.append(item)
            json.dump(discarded_items, open("data/discarded_rules_and_conversations.json", "w"), indent=2)
            print("\n\n")
            continue

        accepted_items.append(item)
        json.dump(accepted_items, open("data/accepted_rules_and_conversations.json", "w"), indent=2)
        print("\n\n")

        #### CHANGE <|USER|>\n into user: (some of the elements are in the wrong format)
