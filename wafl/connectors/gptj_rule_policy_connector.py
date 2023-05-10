from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJRulePolicyConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue: str = None):
        prompt = f"""
The following conversation is taking place:
user: Where is my toy car

The available rules for the user's last utterance are as follows:
1. The user needs to play with a toy car
2. The user wants to fetch a toy car
3. The user wants to check the weather
4. None of the above

Please answer with the most relevant numbers separated by a comma: 1, 2


The following conversation is taking place:
user: hello

The available rules for the user's last utterance are as follows:
1. The user greets
2. The user wants to know the weather
3. None of the above

Please answer with the most relevant numbers separated by a comma: 1


The following conversation is taking place:
user: hello what is the weather like

The available rules for the user's last utterance are as follows:
1. The user greets
2. The user wants to know the weather
3. None of the above

Please answer with the most relevant numbers separated by a comma: 2


The following conversation is taking place:
user: hello
bot: hello there
user: are you a bot 

The available rules for the user's last utterance are as follows:
1. The user greets
2. The user wants to know the weather
3. None of the above

Please answer with the most relevant numbers separated by a comma: 3


The following conversation is taking place:
{dialogue}

The available rules for the user's last utterance are as follows:
{query}
Please answer with the most relevant numbers separated by a comma:
        """.strip()

        return prompt
