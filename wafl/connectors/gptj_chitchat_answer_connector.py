from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJChitChatAnswerConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = (
            f"""
Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction: 
I am talking to a bot. You must reply to all my questions.
If I am making small talk reply with small talk.
If I make a questions you must find the answer in the prior instructions or responses.
Use the prior text to answer my question. The answer might be part of the prior instructions.
If the answer is not in the text, improvise by starting the reply with "I believe". 
If there are multiple questions answer the latest question first.
### Response:
Understood.
{dialogue.replace("user:", "### Instruction:")
         .replace("bot:", "### Response:")
         .replace("The bot remembers:", "Keep in mind that")}
### Response:
        """.strip()
            + "\n"
        )
        return prompt
