import asyncio
import pandas as pd

from wafl.config import Configuration
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector


def get_prompt(df, theme):
    prompt = ""
    for _, row in df.sample(9).iterrows():
        prompt += f"""
<task>
Create a plausible dialogue about the theme \"{row["Theme"]}\" based on the following summary and rules.

The rules are as follows:
{row["Rules"]}

The conversation goes as follows:
{row["Conversation"]}
</task>
        """.strip() + "\n\n"

    return prompt + f"<task>\nCreate plausible dialogue about the theme \"{theme}\" based on the following summary and rules.\n\nThe rules are as follows:\n"


if __name__ == '__main__':
    config = Configuration.load_local_config()
    remote_llm_connector = RemoteLLMConnector(config.get_value("llm_model"), last_strings=["</task>"])

    df = pd.read_csv("data/complex_instructions.csv")
    theme = "playing a song that the user likes"
    prompt = get_prompt(df, theme)
    print(asyncio.run(remote_llm_connector.predict(prompt, temperature=0.5, num_tokens=1500)))
