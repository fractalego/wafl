from dataclasses import dataclass


@dataclass
class Prompt:
    system_prompt: str = ""
    conversation: "Conversation" = None

    def to_dict(self):
        return {
            "system_prompt": self.system_prompt,
            "conversation": self.conversation.to_dict(),
        }


class PrompCreator:
    @staticmethod
    def create(system_prompt: str, conversation: "Conversation") -> Prompt:
        prompt = Prompt()
        prompt.system_prompt = system_prompt
        prompt.conversation = conversation
        return prompt
