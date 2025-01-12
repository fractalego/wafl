from typing import List

from wafl.answerer.entailer import Entailer
from wafl.config import Configuration
from wafl.interface.conversation import Conversation, Utterance


class Selector:
    def __init__(self, config: Configuration):
        self._entailer = Entailer(config)

    async def select_best_answer(
        self, memory: str, rules_text_list: List[str], conversation: Conversation, answers: List[str]
    ):
        memory_scores = [0 for _ in answers]
        rules_score = [0 for _ in answers]
        rules_text = "\n\n".join(rules_text_list)

        for i, answer in enumerate(answers):
            current_conversation = conversation.copy()
            current_conversation.add_utterance(Utterance(answer, "bot"))
            current_conversation_text = (
                f"The conversation goes as follows:\n{current_conversation.to_text()}"
            )
            # memory_scores[i] = await self._entailer.get_score(
            #     f"This is what the bot remembers: {memory}", current_conversation_text
            # )
            rules_score[i] = await self._entailer.get_score(
                f"These are the rules the bot must follow: {rules_text}",
                current_conversation_text,
            )

        best_answer_index = max(
            range(len(answers)), key=lambda i: memory_scores[i] + rules_score[i]
        )
        return answers[best_answer_index]


    #### the rule makes the bot use Bob: when answering questions. it goes on for a long time, forgetting sometimes to follow the rule.
    ### Add a regex to stop the llm: "\n\n[A-Z][a-z]+:"
