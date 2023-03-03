from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJQAConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        text = text.strip()
        text = text.replace("\\'", "'")
        query = query.strip()

        prompt = "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\n" + text + "\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        if dialogue:
            dialogue = dialogue.strip()
            prompt += dialogue + "\n"

        prompt += "Q: " + query + "\n"
        prompt += "A:"
        return prompt
