import asyncio
import pandas as pd

from wafl.config import Configuration
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector
from wafl.retriever.dense_retriever import DenseRetriever


def get_prompt(df, theme, retriever, num_samples):
    indices_and_scores = asyncio.run(retriever.get_indices_and_scores_from_text(theme))
    indices = [index for index, _ in indices_and_scores]
    prompt = ""
    for _, row in df.iloc[indices].sample(num_samples).iterrows():
        prompt += (
            f"""
<task>
Create a plausible dialogue about the theme \"{row["Theme"]}\" based on the following summary and rules.

The rules are as follows:
{row["Rules"]}

The conversation goes as follows:
{row["Conversation"]}
</task>
        """.strip()
            + "\n\n"
        )

    incipit = f"Create plausible dialogue about the theme \"{theme}\" based on the following summary and rules.\n\nThe rules are as follows:\n"

    return (
        prompt
        + f'<task>\n{incipit}'
    )


def generate_conversation(theme, num_samples=2):
    config = Configuration.load_local_config()
    retriever = DenseRetriever("text_embedding_model", config)
    remote_llm_connector = RemoteLLMConnector(
        config.get_value("llm_model"), last_strings=["</task>"], num_replicas=1
    )

    df = pd.read_csv("data/complex_instructions.csv")
    for index, row in df.iterrows():
        asyncio.run(retriever.add_text_and_index(row["Theme"], str(index)))

    prompt = get_prompt(df, theme, retriever, num_samples=num_samples)
    generated_text = asyncio.run(
        remote_llm_connector.predict(prompt, temperature=0.5, num_tokens=2500)
    )[0]
    return "The rules are as follows:\n" + generated_text


if __name__ == "__main__":
    theme = "playing a song that the user likes"
    print(generate_conversation(theme))
