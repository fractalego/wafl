from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJTaskExtractorConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text: str, query: str, dialogue: str = None):
        prompt = (
            f"""
### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: I want to drive the car
</conversation>
### Response:
the user wants to drive the car 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
bot: hello, how can I help
user: Hello
</conversation>
### Response:
[statement] the user says hi 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: goodbye
</conversation>
### Response:
[statement] the user says goodbye
 
### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: hello
user: the user's name is john
</conversation>
### Response:
[statement] the user says their name is John

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: my dog's name is Fido
</conversation>
### Response:
[statement] the user says their dog's name is Fido

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: thank you
</conversation>
### Response:
the user thanks 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: I want to drive a car
bot: do you have a driving license?
user: no
</conversation>
### Response:
the user wants to drive a car 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: I want to drive the car to London
</conversation>
### Response:
the user wants to drive the car to London 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: Can I have french fries
</conversation>
### Response:
the user asks if they can have french fries 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: Add oranges to the shopping list
</conversation>
### Response:
the user wants to add oranges to the shopping list 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: Hello
</conversation>
### Response:
the user greets

### Instruction:
Extract the user's intention from the conversation.
<conversation>
bot: what is your name
user: my name is Alberto
</conversation>
### Response:
[statement] the user says their name is Alberto

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: remember that I am an engineer
</conversation>
### Response:
the user wants the bot to remember that they are an engineer

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: find the user a good restaurant and order a pizza
</conversation>
### Response:
[list of actions] the user wants this bot to find a good restaurant AND the user wants this bot to order a pizza

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: what is the time and how long is it before 12
</conversation>
### Response:
[list of actions] the user wants to know the time AND the user to know how long it is before 12 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: what musing is playing
</conversation>
### Response:
the user wants to know which music is playing 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: what is the the weather like
user: what is the time
### Response:
the user wants to know the time 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: add paper
user: add scissors
user: add stone
</conversation>
the user wants to add stone 

### Instruction:
Extract the user's intention from the conversation.
<conversation>
user: what is the weather what is the temperature
</conversation>
### Response:
[list of actions] the user wants to know the weather AND the user wants to know the temperature

### Instruction:
Extract the user's intention from the conversation.
<conversation>
{dialogue}
</conversation>
### Response: 
        """.strip()
            + "\n"
        )

        return prompt
