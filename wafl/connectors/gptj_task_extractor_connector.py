from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJTaskExtractorConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text: str, query: str, dialogue: str = None):
        prompt = f"""
The task is to extract the user's intention from the last statement from the user.
Prior statements only provide context and should not be used to determine the user's intention.
If the last statement has multiple intentions, separate them with word ANDAND written all in capital letters.
Some examples are below.


The following conversation is taking place:
user: hello what is the weather like

Say the user's intention in the last utterance: the user says hello ANDAND the user asks what the weather is like 


The following conversation is taking place:
user: I want to drive the car

Say the user's intention in the last utterance: the user wants to drive the car 

The following conversation is taking place:
user: I want to see my car
bot: Your car is in the garage
user: I want to drive the car

Say the user's intention in the last utterance: the user wants to drive the car 


The following conversation is taking place:
user: I want to see my car
bot: Your car is in the garage
user: I want to drive the car
user: you

Say the user's intention in the last utterance: unknown 


The following conversation is taking place:
bot: hello there
user: lgdfskaj

Say the user's intention in the last utterance: unknown


The following conversation is taking place:
bot: hello, how can I help
user: Hello

Say the user's intention in the last utterance: the user says hi 


The following conversation is taking place:
user: goodbye

Say the user's intention in the last utterance: the user says goodbye
 

The following conversation is taking place:
user: hello
user: My name is john

Say the user's intention in the last utterance: the user says their name is John


The following conversation is taking place:
user: my dog's name is Fido

Say the user's intention in the last utterance: the user says their dog's name is Fido


The following conversation is taking place:
user: thank you

Say the user's intention in the last utterance: the user thanks 


The following conversation is taking place:
user: I want to drive a car
bot: do you have a driving license?
user: no

Say the user's intention in the last utterance: the user wants to drive a car 


The following conversation is taking place:
user: I want to drive the car to London

Say the user's intention in the last utterance: the user wants to drive the car to London 


The following conversation is taking place:
user: Can I have french fries

Say the user's intention in the last utterance: the user asks if they can have french fries 


The following conversation is taking place:
user: Add oranges to the shopping list

Say the user's intention in the last utterance: the user wants to add oranges to the shopping list 


The following conversation is taking place:
user: Hello

Say the user's intention in the last utterance: the user greets


The following conversation is taking place:
user: what is the weather what is the temperature

Say the user's intention in the last utterance: the user wants to know the weather ANDAND the user wants to know the temperature


The following conversation is taking place:
bot: what is your name
user: my name is Alberto

Say the user's intention in the last utterance: the user says their name is Alberto


The following conversation is taking place:
user: remember that I am an engineer

Say the user's intention in the last utterance: the user wants the bot to remember that they are an engineer


The following conversation is taking place:
user: I want to drive the car to London
bot: here are some routes for you to choose from
bot: london to paris
bot: london to rome
user: find me a good restaurant and order a pizza

Say the user's intention in the last utterance: the user wants this bot to find a good restaurant ANDAND the user wants this bot to order a pizza


The following conversation is taking place:
user: what is the weather like
bot: it is sunny
user: what is the time and how long is it before 12

Say the user's intention in the last utterance: the user wants to know the time ANDAND the user to know how long it is before 12 


The following conversation is taking place:
user: what is the weather like
bot: it is sunny
user: what music is playing

Say the user's intention in the last utterance: the user wants to know which music is playing 


The following conversation is taking place:
user: what is the the weather like
user: what is the time

Say the user's intention in the last utterance: the user wants to know the time 


The following conversation is taking place:
user: add paper
user: add scissors
user: add stone

Say the user's intention in the last utterance: the user wants to add stone 


The following conversation is taking place:
{dialogue}

Say the user's intention in the last utterance: 
        """.strip()

        return prompt
