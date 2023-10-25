import asyncio
import os
import re

from wafl.connectors.bridges.bridge_implementation import load_knowledge_from_file
from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMChitChatAnswerBridge:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = f"""
The following is a summary of a conversation. All the elements of the conversation are described briefly:
{text}
Rules:
a) If the following applies: "The user wants to run a code" then follow all the steps below from top to bottom. 
    Do *not* skip any step. Each step is a new interaction with the user. Do not complete more than one step at a time.
    Step 1a: If the code does not exist write it out.
    Output the dialogue above and then write STEP 1a FINISHED on a new line.
    
    Step 2a: If the code already exists in the conversation ask the user if they want to change something in the code.
    Output the dialogue above and then write STEP 2a FINISHED on a new line.

    Step 3a: If the user still wants to go ahead, wrap the full code the xml tag <execute> ... </execute>.
            example: <execute>print("hello world")</execute> (the code inside the tags can be any valid python code)
    Output the dialogue above and then write STEP 3a FINISHED on a new line.

Create a plausible dialogue based on the aforementioned summary. 
Do not repeat yourself. Be friendly but not too servile.
Wrap any code or html you output in the with the markdown syntax for code blocks (i.e. use triple backticks ```).
  
This is the dialogue:
{dialogue}
bot:
        """.strip()
        return prompt
