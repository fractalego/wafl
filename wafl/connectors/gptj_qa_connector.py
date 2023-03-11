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
        prompt += "Story:\n\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the capital of Italy?\n"
        prompt += "A: [*not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\nWater is wet\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: Is the earth round?\n"
        prompt += "A: [*not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\nThe user says 'hello'. The bot answers 'hello there'. \n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the size of Jupyter?\n"
        prompt += "A: [*not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\nThe user says 'hello'. The bot answers 'hello there'. The bot remembers: The sun is shiny\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: How is the sun?\n"
        prompt += "A: [*in* the story] shiny\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += (
            "Story:\nThe user says 'hello'. The bot answers 'hello there'."
            "When asked the user's name the user replies: I am John\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user's name?\n"
        prompt += "A: [*in* the story] John\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\nThe user says 'hello'\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user's name?\n"
        prompt += "A: [*not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\nThe user says 'it is raining'\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What does the user want to do?\n"
        prompt += "A: [*not* in the story] unknown\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\nThe user says 'hello'. The bot answers 'hello there'. "\
                  "When the bot asks who is president, the user replies JFK\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: Who is the president?\n"
        prompt += "A: [*is* in the story] JFK\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\nThe user says 'hello'. The bot answers 'hello there'. " \
                  "When the bot asks what the user is reading, the user replies a book\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user reading?\n"
        prompt += "A: [*is* in the story] a book\n\n"

        prompt += "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\n" + text + "\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        if dialogue:
            dialogue = dialogue.strip()
            prompt += dialogue + "\n"

        prompt += "Q: " + query + "\n"
        prompt += "A:"
        return prompt
