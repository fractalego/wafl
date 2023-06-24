from wafl.connectors.base_llm_connector import BaseLLMConnector


class LLMTaskExtractorConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)

    async def _get_answer_prompt(self, text: str, query: str, dialogue: str = None):
        prompt = f"""
The task is to extract the user's intention from the last statement from the user.
Prior statements only provide context and should not be used to determine the user's intention.
Be as specific as possible.
If the last statement has multiple intentions, separate them with a semicolon ";".
After the task is extracted, end the text with <|EOS|>.
Some examples are below.


The following conversation is taking place:
user: I want to drive the car

Say the user's intention in the last utterance: the user wants to drive the car<|EOS|>


The following conversation is taking place:
user: I want to see my car
bot: Your car is in the garage
user: I want to drive it

Say the user's intention in the last utterance: the user wants to drive the car<|EOS|>


The following conversation is taking place:
user: I want to see my car
bot: Your car is in the garage
user: I want to drive the car
user: you

Say the user's intention in the last utterance: unknown<|EOS|>


The following conversation is taking place:
user: you

Say the user's intention in the last utterance: unknown<|EOS|>


The following conversation is taking place:
user: what

Say the user's intention in the last utterance: unknown<|EOS|>



The following conversation is taking place:
bot: hello there
user: lgdfskaj

Say the user's intention in the last utterance: unknown<|EOS|>
 

The following conversation is taking place:
user: I want to drive the car to London

Say the user's intention in the last utterance: the user wants to drive the car to London<|EOS|>


The following conversation is taking place:
user: Can I have french fries

Say the user's intention in the last utterance: the user asks if they can have french fries<|EOS|>


The following conversation is taking place:
user: Add oranges to the shopping list

Say the user's intention in the last utterance: the user wants to add oranges to the shopping list<|EOS|>


The following conversation is taking place:
user: Hello
bot: hello
user: what is in the shopping list
bot: the shopping list contains apples, kiwis
user: right, add oranges

Say the user's intention in the last utterance: the user wants to add oranges to the shopping list<|EOS|>


The following conversation is taking place:
user: what is the weather and what is the temperature

Say the user's intention in the last utterance: the user wants to know the weather ; the user wants to know the temperature<|EOS|>


The following conversation is taking place:
user: remember that I am an engineer

Say the user's intention in the last utterance: the user wants the bot to remember that they are an engineer<|EOS|>


The following conversation is taking place:
user: I want to drive the car to London
bot: here are some routes for you to choose from
bot: london to paris
bot: london to rome
user: find me a good restaurant and order a pizza

Say the user's intention in the last utterance: the user wants this bot to find a good restaurant ; the user wants this bot to order a pizza<|EOS|>


The following conversation is taking place:
user: what is the weather like
bot: it is sunny
user: what is the time and how long is it before 12

Say the user's intention in the last utterance: the user wants to know the time ; the user to know how long it is before 12<|EOS|>


The following conversation is taking place:
user: tell me what time it is and then what is the weather tomorrow

Say the user's intention in the last utterance: the user wants to know the time ; the user wants to know the weather tomorrow<|EOS|>


The following conversation is taking place:
user: what is the weather like
bot: it is sunny
user: what music is playing

Say the user's intention in the last utterance: the user wants to know which music is playing<|EOS|>


The following conversation is taking place:
user: what is the the weather like
user: what is the time

Say the user's intention in the last utterance: the user wants to know the time<|EOS|>


The following conversation is taking place:
user: tell me about the weather.

Say the user's intention in the last utterance: the user wants to know what the weather is like<|EOS|>


The following conversation is taking place:
user: My name is John

Say the user's intention in the last utterance: unknown<|EOS|>


The following conversation is taking place:
user: add paper
user: add scissors
user: add stone

Say the user's intention in the last utterance: the user wants to add stone<|EOS|>


The following conversation is taking place:
user: list all the files in a folder

Say the user's intention in the last utterance: the user wants list all the files in a folder<|EOS|>


The following conversation is taking place:
{dialogue}

Say the user's intention in the last utterance: 
        """.strip()

        return prompt
