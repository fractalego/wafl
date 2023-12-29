import os

from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory

_path = os.path.dirname(__file__)


class Entailer:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config

    async def left_entails_right(self, lhs: str, rhs: str, dialogue: str) -> str:
        prompt = await self._get_answer_prompt(lhs, rhs, dialogue)
        result = await self._connector.generate(prompt)
        result = self._clean_result(result)
        return result == "yes"

    async def _get_answer_prompt(self, lhs, rhs, dialogue):
        prompt = f"""
<task>
This is a conversation between two agents ("bot" and "user"):
bot: what can I do for you?

Given this dialogue, the task is to determine whether the following two utterances have the same meaning:  
1) user: I need to book a flight to Paris.
2) user: I'd like to buy a plane ticket to paris.
Please answer "yes" or "no": yes
</task>

<task>
This is a conversation between two agents ("bot" and "user"):
{dialogue}

Given this dialogue, the task is to determine whether the following two utterances have the same meaning:  
1) {lhs.lower()}
2) {rhs.lower()}
Please answer "yes" or "no": 
        """.strip()
        return prompt

    def _clean_result(self, result):
        result = result.replace("</task>", "")
        result = result.split("\n")[0]
        result = result.strip()
        return result.lower()
