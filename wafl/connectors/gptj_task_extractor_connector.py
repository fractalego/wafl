from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJTaskExtractorConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        if not dialogue:
            return ""

        dialogue_str = "\n".join(dialogue)
        prompt = f"""
The following conversation is taking place:
{dialogue_str}

What is the task the user wants to accomplish?
        """.strip()

        return prompt
