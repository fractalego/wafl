from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJAnswerPolicyConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        if not dialogue:
            return "Say No 5 times: No No No "

        dialogue_str = "\n".join(dialogue)
        prompt = f"""
The following conversation is taking place:
User: I have a toy car

Is the next item fit to continue the conversation?
Bot: The weather looks rainy

Please answer Yes or No: n


The following conversation is taking place:
User: I am hungry

Is the next item fit to continue the conversation?
Bot: This is the menu

Please answer Yes or No: y


The following conversation is taking place:
User: blah blah

Is the next item fit to continue the conversation?
Bot: I don't understand

Please answer Yes or No: y


The following conversation is taking place:
{dialogue_str}

Is the next item fit to continue the conversation?
bot: {query}

Please answer Yes or No:
        """.strip()

        return prompt
