from dataclasses import dataclass

from wafl.interface.conversation import Conversation, Utterance


@dataclass
class PromptTemplate:
    system_prompt: str = ""
    conversation: "Conversation" = None

    def to_dict(self):
        return {
            "system_prompt": self.system_prompt,
            "conversation": self.conversation.to_dict() if self.conversation else [],
        }


class PromptCreator:
    @staticmethod
    def create(system_prompt: str, conversation: Conversation) -> PromptTemplate:
        prompt = PromptTemplate()
        prompt.system_prompt = system_prompt
        prompt.conversation = conversation
        return prompt

    @staticmethod
    def create_from_one_instruction(instruction: str) -> PromptTemplate:
        return PromptTemplate(
            system_prompt="",
            conversation=Conversation(
                utterances=[Utterance(speaker="user", text=instruction)]
            ),
        )
