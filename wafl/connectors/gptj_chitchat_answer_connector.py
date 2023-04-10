from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJChitChatAnswerConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = f"""
### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
user: hello there
### Response:
bot: [small talk] hello there
        
### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
user: what is the color of the sun
The bot remembers: the sun is bright yellow
### Response:
bot: I remember that the sun is bright yellow

### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
user: what is the height of my truck
The bot remembers: the user's truck is 8ft
### Response:
bot: I remember that the user's truck is 8ft

### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
user: what is the colour of the sky
The bot remembers: the user's truck is 8ft
### Response:
bot: I believe it is blue on a nice day

### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
user: what is the name of the lead actor in Superman (1978)
### Response:
bot: I believe it is Christopher Reeve

### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
user: My flat is a one bedroom
bot: nice to know
user: is my flat a 2 bedroom
### Response:
bot: [answer in conversation] no, you said it is a 1 bedroom

### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
user: what is the date today
bot: today is 17 April 2023
user: thank you
user: what is the date today?
### Response:
bot: [answer in conversation] I said the date is 17 April 2023

### Input:
user: Hello !
bot: The weather is very cold
bot: The temperature today is 0 celsius
user: What is the temperature today ?
### Response:
bot: [answer in conversation] I said the temperature is 0 Celsius

### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
the bot remembers: the user's name is John
user: is my name Jane
### Response:
bot: [answer in conversation] no, you said your name is John

### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
user: my name is John
bot: good to know
user: what is the user's name
### Response:
bot: [answer in conversation] you said your name is John

### Instruction:
A user is speaking to a bot. Find the best reply the bot can give. 
Use what the bot remembers as well as the conversation to answer the questions.
If the answer is not in the text, improvise by starting the reply with "I believe".
If the user is making small talk, just reply in tone.
### Input:
{dialogue}
### Response:
bot:
        """.strip()
        return prompt
