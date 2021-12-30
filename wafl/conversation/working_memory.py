class WorkingMemory:
    def __init__(self):
        self._story = ""
        self._questions = []
        self._answers = []

    def get_story(self):
        return self._story

    def get_discussion(self):
        discussion = ""
        for question, answer in zip(self._questions, self._answers + [""]):
            discussion += "Q: " + question + "\n"
            discussion += "A: " + answer + "\n"

        return discussion

    def add_story(self, text):
        if text[-1] != ".":
            text += "."

        self._story += " " + text

    def add_question(self, text):
        self._questions.append(text)

    def add_answer(self, text):
        self._answers.append(text)
