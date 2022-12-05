class ConversationalMemory:
    def __init__(self):
        self._story = ""
        self._questions = []
        self._answers = []
        self._failed_clauses = set()

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

    def text_is_in_prior_questions(self, text: str):
        for question in self._questions:
            if text.lower() in question.lower():
                return True

        return False

    def text_is_in_prior_answers(self, text: str):
        for answer in self._answers:
            if text.lower() in answer.lower():
                return True

        return False

    def add_failed_clause(self, clause):
        self._failed_clauses.add(clause)

    def is_in_prior_failed_clauses(self, clause):
        return clause in self._failed_clauses

    def erase(self):
        self._story = ""
        self._questions = []
        self._answers = []
        self._failed_clauses = set()
