from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJAnswerPolicyConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue: str = None):
        if not dialogue:
            return "Say yes 5 times: yes yes yes "

        prompt = f"""
### Instruction:
A conversation is taking place between a user and a bot. 
The last line is a candidate reply from the bot. 
Is this reply fit to continue the conversation?  
Reply "yes" or "no".
### Input:
user: I have a toy car
Bot: The weather looks rainy
### Response:
n

### Instruction:
A conversation is taking place between a user and a bot. 
The last line is a candidate reply from the bot. 
Is this reply fit to continue the conversation?  
Reply "y" for yes or "n" for no.
### Input:
bot: I have a toy car
user: what
bot: I have a toy car
### Response:
y

### Instruction:
A conversation is taking place between a user and a bot. 
The last line is a candidate reply from the bot. 
Is this reply fit to continue the conversation?  
Reply "y" for yes or "n" for no.
### Input:
user: I am hungry
bot: This is the menu
### Response:
y

### Instruction:
A conversation is taking place between a user and a bot. 
The last line is a candidate reply from the bot. 
Is this reply fit to continue the conversation?  
Reply "y" for yes or "n" for no.
### Input:
user: blah blah
bot: I don't understand
### Response:
y

### Instruction:
A conversation is taking place between a user and a bot. 
The last line is a candidate reply from the bot. 
Is this reply fit to continue the conversation?  
Reply "y" for yes or "n" for no.
### Input:
user: blah blah
bot: the bot understands that the user says blah blah  
### Response:
y

### Instruction:
A conversation is taking place between a user and a bot. 
The last line is a candidate reply from the bot. 
Is this reply fit to continue the conversation?  
Reply "y" for yes or "n" for no.
### Input:
the bot remembers: the user's name is John
user: is my name Jane
bot: no
### Response:
y

### Instruction:
A conversation is taking place between a user and a bot. 
The last line is a candidate reply from the bot. 
Is this reply fit to continue the conversation?  
Reply "y" for yes or "n" for no.
### Input:
{dialogue}
bot: {query}
### Response:
        """.strip() + "\n"

        return prompt
