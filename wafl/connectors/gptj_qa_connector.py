from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJQAConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        text = text.strip()
        text = text.replace("\\'", "'")
        query = query.strip()

        prompt = "Below two people discuss a story. If the answer is not in the story the answer is 'unknown'.\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "<story> </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the capital of Italy?\n"
        prompt += "A: [the answer is *not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "<story> Water is wet </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: Is the earth round?\n"
        prompt += "A: [the answer is *not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += (
            "<story> The user says 'hello'. The bot answers 'hello there'</story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the size of Jupyter?\n"
        prompt += "A: [the answer is *not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "<story> The user says 'hello'. The bot answers 'hello there'. The bot remembers: The sun is shiny </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: How is the sun?\n"
        prompt += "A: [the answer is in the story] shiny\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += (
            "<story> The user says 'hello'. The bot answers 'hello there'."
            "When asked the user's name the user replies: I am John </story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user's name?\n"
        prompt += "A: [the answer is in the story] John\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "<story> The user says 'hello' </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user's name?\n"
        prompt += "A: [the answer is *not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "<story> The user says 'it is raining' </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What does the user want to do?\n"
        prompt += "A: [the answer is *not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += (
            "<story> The user says 'hello'. The bot answers 'hello there'. "
            "When the bot asks who is president, the user replies JFK </story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: Who is the president?\n"
        prompt += "A: [the answer is in the story] JFK\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += (
            "<story> The user says 'hello'. The bot answers 'hello there'. "
            "When the bot asks what the user is reading, the user replies a book </story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user reading?\n"
        prompt += "A: [the answer is in the story] a book\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "<story> " + text + " </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        if dialogue:
            dialogue = dialogue.strip()
            prompt += dialogue + "\n"

        prompt += "Q: " + query + "\n"
        prompt += "A:"
        return prompt
