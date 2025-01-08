from wafl.answerer.entailer import Entailer
from wafl.config import Configuration
from wafl.interface.conversation import Conversation, Utterance


class Selector:
    def __init__(self, config: Configuration):
        self._entailer = Entailer(config)

    def select_best_answer(
        self, memory: str, rules_text: str, conversation: Conversation, answers
    ):
        memory_scores = [0 for _ in answers]
        rules_score = [0 for _ in answers]

        for i, answer in enumerate(answers):
            current_conversation = conversation.copy()
            current_conversation.add_utterance(Utterance(answer, "bot"))
            current_conversation_text = (
                f"The conversation goes as follows:\n{current_conversation}"
            )
            memory_scores[i] = self._entailer.get_score(
                f"This is what the bot remembers: {memory}", current_conversation_text
            )
            rules_score[i] = self._entailer.get_score(
                f"These are the rules the bot must follow: {rules_text}",
                current_conversation_text,
            )

        best_answer_index = max(
            range(len(answers)), key=lambda i: memory_scores[i] + rules_score[i]
        )
        return answers[best_answer_index]
