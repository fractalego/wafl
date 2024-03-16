import json

from tqdm import tqdm
from wafl.config import Configuration
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector
from wafl.retriever.dense_retriever import DenseRetriever


def find_all_occurences(sentence, word):
    import re
    return [match.start() for match in re.finditer(word, sentence)]


if __name__ == "__main__":
    config = Configuration.load_local_config()
    retriever = DenseRetriever("text_embedding_model", config)
    stopwords = ["</task>", "<assistant>", "<|assistant|>", "</s>"]
    remote_llm_connector = RemoteLLMConnector(
        config.get_value("llm_model"), last_strings=stopwords
    )

    data = json.load(open("data/to_modify_negative_examples.json"))
    output_data = []
    for text in tqdm(data):
        conversation = text
        all_new_lines = find_all_occurences(conversation, "\n")
        for new_line in all_new_lines:
            tail = conversation[new_line:]
            if len(tail) > len(conversation)/10. and tail in text[:new_line]:
                conversation = conversation[:new_line]
                break

        output_data.append(conversation)

    json.dump(output_data, open("data/negative_examples.json", "w"), indent=2)