from wafl.connectors.base_llm_connector import BaseLLMConnector


class GPTJQAConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        text = text.strip()
        text = text.replace("\\'", "'")
        query = query.strip()

        prompt = "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += "<story> </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the capital of Italy?\n"
        prompt += "A: unknown\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += "<story> Water is wet </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: Is the earth round?\n"
        prompt += "A: unknown\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += (
            "<story> The user says 'hello'. The bot answers 'hello there'</story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the size of Jupyter?\n"
        prompt += "A: unknown\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += (
            "<story> The user says 'find me a restaurant'</story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user asking the bot?\n"
        prompt += "A: to find a restaurant\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += (
            "<story> The user says 'I live at 1km from here'</story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: How far from here?\n"
        prompt += "A: 1 kilometer\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += (
            "<story> The user says 'hello'.</story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: what is the name of the user?\n"
        prompt += "A: unknown\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += "<story> The user says 'hello'. The bot answers 'hello there'. The bot remembers: The sun is shiny </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: How is the sun?\n"
        prompt += "A: shiny\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += (
            "<story> The user says 'hello'. The bot answers 'hello there'."
            "When asked the user's name the user replies: I am John </story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user's name?\n"
        prompt += "A: John\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += "<story> The user says 'hello' </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user's name?\n"
        prompt += "A: unknown\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += "<story> The user says 'it is raining' </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What does the user want to do?\n"
        prompt += "A: unknown\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += (
            "<story> The user says 'hello'. The bot answers 'hello there'. "
            "When the bot asks who is president, the user replies JFK </story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: Who is the president?\n"
        prompt += "A: JFK\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += (
            "<story> The user says 'hello'. The bot answers 'hello there'. "
            "When the bot asks what the user is reading, the user replies a book </story>\n\n"
        )
        prompt += "The first person asks questions about the story and the second answers them:\n"
        prompt += "Q: What is the user reading?\n"
        prompt += "A: a book\n\n"

        prompt += "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += "<story> " + text + " </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        if dialogue:
            dialogue = dialogue.strip()
            prompt += dialogue + "\n"

        prompt += "Q: " + query + "\n"
        prompt += "A:"
        return prompt
