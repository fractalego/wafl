from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJTaskExtractorConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text: str, query: str, dialogue: str = None):
        prompt = f"""
The following conversation is taking place:
user: I want to drive the car

Say the user's intention: the user wants to drive the car 


The following conversation is taking place:
user: I want to drive a car
bot: do you have a driving license?
user: no

Say the user's intention: the user wants to drive a car 


The following conversation is taking place:
user: I want to drive the car to London

Say the user's intention: the user wants to drive the car to London 


The following conversation is taking place:
user: Can I have french fries

Say the user's intention: the user asks if they can have french fries 


The following conversation is taking place:
user: Add oranges to the shopping list

Say the user's intention: the user wants to add oranges to the shopping list 


The following conversation is taking place:
user: Hello

Say the user's intention: the user greets


The following conversation is taking place:
bot: what is your name
user: my name is Alberto

Say the user's intention: the user says their name is Alberto


The following conversation is taking place:
{dialogue}

Say the user's intention: 
        """.strip()

        return prompt