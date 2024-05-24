import os
import textwrap

from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.connectors.prompt_template import PromptTemplate

_path = os.path.dirname(__file__)


class LLMChitChatAnswerClient:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config

    async def get_answer(self, text: str, dialogue: str) -> str:
        prompt = await self._get_answer_prompt(text, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(
        self, text: str, dialogue: "Conversation" = None
    ) -> PromptTemplate:
        return PromptTemplate(
            system_prompt=self._get_prompt_text(text), conversation=dialogue
        )

    def _get_prompt_text(self, text):
        return textwrap.dedent(
            f"""
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
"""
        )
