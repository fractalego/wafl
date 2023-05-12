from wafl.connectors.base_llm_connector import BaseLLMConnector


class LLMRulePolicyConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue: str = None):
        prompt = f"""
The task is to map the user's last utterance to the most relevant sentences from a list of sentences. 
The two sentences are considered similar if they have similar meaning.
The most similar sentences are the one that should be selected.
There can be more than one selection.
The dialogue provides a context for the choice.
        
        
The following conversation is taking place between a user and a bot:
user: Where is my toy car

The available choices to map the user's last utterance are as follows:
1. The user needs to play with a toy car
2. The user wants to fetch a toy car
3. The user wants to check the weather
4. None of the above

Please answer with the most relevant numbers separated by a comma: 1, 2


The following conversation is taking place between a user and a bot:
user: Where is my toy car
the bot understands the task to be the user wants to fetch a toy car

The available choices to map the user's last utterance are as follows:
1. The user needs to play with a toy car
2. The user wants to fetch a toy car
3. The user wants to check the weather
4. None of the above

Please answer with the most relevant numbers separated by a comma: 2


The following conversation is taking place between a user and a bot:
user: hello

The available choices to map the user's last utterance are as follows:
1. The user greets
2. The user wants to know the weather
3. None of the above

Please answer with the most relevant numbers separated by a comma: 1


The following conversation is taking place between a user and a bot:
user: what is the weather like

The available choices to map the user's last utterance are as follows:
1. The user greets
2. The user says: "what is the weather like"
3. None of the above

Please answer with the most relevant numbers separated by a comma: 2


The following conversation is taking place between a user and a bot:
user: hello

The available choices to map the user's last utterance are as follows:
1. The user says "hello"
2. The user says: "what is the weather like"
3. None of the above

Please answer with the most relevant numbers separated by a comma: 1


The following conversation is taking place between a user and a bot:
user: hello what is the weather like

The available choices to map the user's last utterance are as follows:
1. The user greets
2. The user wants to know the weather
3. None of the above

Please answer with the most relevant numbers separated by a comma: 2


The following conversation is taking place between a user and a bot:
user: hello
bot: hello there
user: are you a bot 

The available choices to map the user's last utterance are as follows:
1. The user greets
2. The user wants to know the weather
3. None of the above

Please answer with the most relevant numbers separated by a comma: 3


The following conversation is taking place between a user and a bot:
user: thank this bot

The available choices to map the user's last utterance are as follows:
1. The user says: "thank this bot"
2. The user asks about the weather
3. None of the above

Please answer with the most relevant numbers separated by a comma: 1


The following conversation is taking place between a user and a bot:
user: shut up

The available choices to map the user's last utterance are as follows:
1. The user asks about the weather
2. The user says: "shut up"
3. None of the above

Please answer with the most relevant numbers separated by a comma: 2


The following conversation is taking place between a user and a bot:
{dialogue}

The available choices to map the user's last utterance are as follows:
{query}

Please answer with the most relevant numbers separated by a comma:
        """.strip()

        return prompt
