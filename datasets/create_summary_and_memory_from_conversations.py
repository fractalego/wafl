import asyncio
import json
import re

from wafl.config import Configuration
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector
from wafl.retriever.dense_retriever import DenseRetriever

_max_rows = 2000
items = json.load(open("data/accepted_rules_and_conversations.json"))


def get_prompt(conversation_item):
    return f"""
Your task is to read the following conversation and create a summary of the knowledge that is being shared.
Specifically, you must create a summary of the bot's knowledge that is being shared in the conversation.
The conversation follow some rules explained at the beginning of the conversation. 
Never *under any circumstance* include in the summary the rules that are explained at the beginning of the conversation.
Do not include in the summary the conversation itself, just what the bot seem to know given its answers.
If the bot outputs a text withing the tags <memory> and </memory> or <remember> and </remember> include that text in the summary.
The text containing the rules and the conversation is as follows:
<text> 
{conversation_item}
</text>

Summary of the bot's knowledge:
    """.strip()


def clean_summary(summary):
    return summary.replace("</s>", "")


def clean_conversation_item(item):
    # Change <|USER|>\n into user
    item = item.replace("<|USER|>\n", "user: ")
    item = item.replace("<|BOT|>\n", "bot: ")

    # Change <memory>function()</memory> into <memory><execute>function()</execute></memory> if there is a python function call being made
    #item = re.sub("<memory>(.*?)\s(.*?\()(.*?)</memory>", r"<memory>\1 <execute>\2\3</execute></memory>", item)
    #item = re.sub("<remember>(.*?)\s(.*?\()(.*?)</remember>", r"<remember>\1 <execute>\2\3</execute></remember>", item)

    # some sentences are between [] and should be removed
    item = re.sub(r"\[.*?\]", "", item)

    # sometimes at the end of the conversation the bot says "Process finished with exit code 0". Erase this
    item = re.sub(r"Process finished with exit code 0", "", item)

    # todo User -> user, or at least be internally consistent
    item = item.replace("User: ", "user: ")

    return item


if __name__ == "__main__":
    config = Configuration.load_local_config()
    retriever = DenseRetriever("text_embedding_model", config)
    remote_llm_connector = RemoteLLMConnector(
        config.get_value("llm_model"), last_strings=["</task>"]
    )

    complete_items = []
    for item in items:
        item = clean_conversation_item(item)
        summary = asyncio.run(
            remote_llm_connector.predict(get_prompt(item), temperature=0.5, num_tokens=2500)
        )[0]
        summary = clean_summary(summary)
        complete_items.append(f"This is the summary of the bot's knowledge: {summary}\n\n{item}")
        json.dump(complete_items, open("data/summary_and_memory_from_conversations.json", "w"), indent=2)

