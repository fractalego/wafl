import asyncio
import json
from fuzzywuzzy import fuzz
from tqdm import tqdm

from wafl.config import Configuration
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector
from wafl.retriever.dense_retriever import DenseRetriever


def get_new_task():
    return (
        "\n\n"
        "<task>\n"
        "Write a conversation exactly like the old one with one exception:\n"
        "You *must* insert in the middle of the conversation a function to be executed\n"
        "For example, if a conversation is about fruits, you can insert a function that calculates the number of fruits like this <execute>number_of_fruits()</execute>\n"
        "You can use the tags <execute> and </execute> to insert the function or <function> and </function> or <f> and </f>\n, or <run> and </run>. Choose randomly.\n"
        "Show the results below and end with the tag </task>:\n"
    )


def get_prompt_before_conversation(text):
    pattern = "\nThe conversation goes as follows:\n"
    return text.split(pattern)[0] + pattern


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

    output_data = json.load(open("data/tmp_negative_examples.json"))
    for text_positive, text_negative in zip(data_positive, data_negative):
        to_save = get_prompt_before_conversation(text_positive)
        to_save += get_conversation(text_negative)
        output_data.append(to_save)

    json.dump(output_data, open("data/negative_examples.json", "w"), indent=2)