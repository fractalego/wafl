from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJQAConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        text = text.strip()
        text = text.replace("\\'", "'")
        query = query.strip()

        prompt = (
            f"""
Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
Use the following pieces of context to answer the question at the end. If you are even a little unsure about the answer just say "unknown", never try to make up an answer.
Do not conversate. Do not give explanation. Do not improvise. Just use the words in the context if the answer is there. 
This is the only context you know is the following conversation, you have no other knowledge: 
{text}.
The question is: {query}.
### Response:
        """.strip()
            + "\n"
        )
        return prompt
