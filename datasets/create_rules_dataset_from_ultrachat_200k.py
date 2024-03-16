import json

import pandas as pd
from tqdm import tqdm

from create_rules_dataset import generate_conversation
from wafl.config import Configuration
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector
from wafl.retriever.dense_retriever import DenseRetriever

_max_rows = 2000


def conversation_is_valid(conversation):
    if "\nuser: " not in conversation:
        return False

    if "- The user " not in conversation:
        return False

    return True


def clean_conversation(conversation):
    conversation = conversation.replace("</s>", "")
    conversation = conversation.replace("</task>", "")
    return conversation


if __name__ == "__main__":
    config = Configuration.load_local_config()
    retriever = DenseRetriever("text_embedding_model", config)
    remote_llm_connector = RemoteLLMConnector(
        config.get_value("llm_model"), last_strings=["</task>"]
    )

    df = pd.read_parquet("data/train_gen-00000-of-00003-a6c9fb894be3e50b.parquet")
    dataset_items = json.load(open("data/rules_and_conversations.json"))
    for index, row in tqdm(df[len(dataset_items):_max_rows + len(dataset_items)].iterrows(), total=_max_rows):
        theme = row["prompt"]
        conversation = generate_conversation(theme, num_samples=3)
        if not conversation_is_valid(conversation):
            continue

        if conversation in dataset_items:
            continue

        conversation = clean_conversation(conversation)
        dataset_items.append(conversation)
        json.dump(dataset_items, open("data/rules_and_conversations.json", "w"), indent=2)
