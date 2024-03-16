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
        "Write a conversation that does not follow the same pattern as the previous one.\n"
        "You must create a new conversation starting as the old one.\n"
        "In particular, the new conversation between the user and the bot does not follow and contraddicts the rules and information above.\n"
        "You can keep the conversation as it is but without any <> tags\n"
        "You can also use the wrong tags.\n"
        "You can also create a conversation that contradicts the rules above.\n"
        "Show the results below, write at most 10 lines and end with the tag </task>:\n"
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

    data = json.load(open("data/positive_examples.json"))
    output_data = json.load(open("data/tmp_negative_examples.json"))
    tags = ["<execute>", "<memory>", "<remember>", "<run>", "<store>", "<function>", "<f>", "<bash>",
            "</execute>", "</memory>", "</remember>", "</run>", "</store>", "</function>", "</f>", "</bash>"
            ]
    for text in tqdm(data[len(output_data):]):
        text += get_new_task()
        to_save = ""
        while len(to_save) < 200 or to_save in text or fuzz.ratio(to_save, get_conversation(text)) > 90:
            conversation = asyncio.run(remote_llm_connector.predict(text, num_tokens=2048, num_replicas=1))
            to_save = conversation[0]
            for item in stopwords:
                to_save = to_save.replace(item, "")
                to_save = to_save.split("<task>")[0]

        for item in tags:
            to_save = to_save.replace(item, "")

        output_data.append(to_save)
        json.dump(output_data, open("data/tmp_negative_examples.json", "w"), indent=2)

    data = json.load(open("data/positive_examples.json"))
    output_data = json.load(open("data/tmp_negative_examples.json"))
    negative_data = []
    for positive, negative in zip(data, output_data):
        prompt = get_prompt_before_conversation(positive)
        if prompt not in negative:
            negative = prompt + negative
        negative_data.append(negative)

    json.dump(negative_data, open("data/negative_examples.json", "w"), indent=2)