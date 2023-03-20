from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJAnswerPolicyConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        if not dialogue:
            return "Say yes 5 times: yes yes yes "

        dialogue_str = "\n".join(dialogue)
        prompt = f"""
The following conversation is taking place:
user: I have a toy car

Is the next item fit to continue the conversation?
Bot: The weather looks rainy

Please answer Yes or No: n


The following conversation is taking place:
bot: I have a toy car
user: what

Is the next item fit to continue the conversation?
bot: I have a toy car

Please answer Yes or No: y


The following conversation is taking place:
user: I am hungry

Is the next item fit to continue the conversation?
bot: This is the menu

Please answer Yes or No: y


The following conversation is taking place:
user: blah blah

Is the next item fit to continue the conversation?
bot: I don't understand

Please answer Yes or No: y


The following conversation is taking place:
{dialogue_str}

Is the next item fit to continue the conversation?
bot: {query}

Please answer Yes or No:
        """.strip()

        return prompt
