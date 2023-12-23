import os

from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory

_path = os.path.dirname(__file__)


class LLMChitChatAnswerBridge:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text, rules_text, dialogue=None):
        prompt = f"""
The following is a summary of a conversation. All the elements of the conversation are described briefly:
<summary>        
A user is chatting with a bot. The chat is happening through a web interface. The user is typing the messages and the bot is replying.
{text.strip()}
</summary>

<instructions>
Create a plausible dialogue based on the aforementioned summary and rules. 
Do not repeat yourself. Be friendly but not too servile.
Wrap any code or html you output in the with the markdown syntax for code blocks (i.e. use triple backticks ```) unless it is between <execute> tags.
</instructions>

This is the dialogue:
{dialogue}
bot:
        """.strip()
        return prompt
