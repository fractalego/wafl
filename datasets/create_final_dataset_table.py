import json

import pandas as pd

from datasets import load_dataset

from wafl.config import Configuration
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector
from wafl.retriever.dense_retriever import DenseRetriever


def get_memory(text):
    start_pattern = "This is the summary of the bot's knowledge: \n"
    end_pattern = "\nThe rules are as follows:\n"
    return text[text.find(start_pattern) + len(start_pattern) : text.find(end_pattern)]


def get_rules(text):
    start_pattern = "\nThe rules are as follows:\n"
    end_pattern = "\nThe conversation goes as follows:\n"
    return text[text.find(start_pattern) + len(start_pattern) : text.find(end_pattern)]


def get_conversation(text):
    pattern = "\nThe conversation goes as follows:\n"
    return text.split(pattern)[1]


if __name__ == "__main__":
    config = Configuration.load_local_config()
    retriever = DenseRetriever("text_embedding_model", config)
    stopwords = ["</task>", "<assistant>", "<|assistant|>", "</s>"]
    remote_llm_connector = RemoteLLMConnector(
        config.get_value("llm_model"), last_strings=stopwords
    )

    data_positive = json.load(open("data/positive_examples.json"))
    data_negative = json.load(open("data/to_modify_negative_examples.json"))
    output_dict = {"memory": [], "rules": [], "positive_conversation": [], "negative_conversation": []}
    for text_positive, text_negative in zip(data_positive, data_negative):
        memory = get_memory(text_positive)
        rules = get_rules(text_positive)
        positive_conversation = get_conversation(text_positive)
        negative_conversation = get_conversation(text_negative)
        output_dict["memory"].append(memory)
        output_dict["rules"].append(rules)
        output_dict["positive_conversation"].append(positive_conversation)
        output_dict["negative_conversation"].append(negative_conversation)

    df = pd.DataFrame(output_dict)
    df.to_parquet("data/wafl_functions.parquet", index=False)
    dataset = load_dataset("parquet", data_files="data/wafl_functions.parquet")
    dataset.push_to_hub("fractalego/wafl-functions-dataset")
    print("Dataset pushed to the hub")