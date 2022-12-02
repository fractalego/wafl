from wafl.conversation.utils import is_question


class Narrator:
    def summarize_dialogue(self, dialogue_list):
        summary = ""
        for line in dialogue_list:
            speaker = self.get_speaker(line)
            utterance = self.get_utterance(line)
            if not speaker or not utterance:
                continue

            if is_question(line):
                summary += f"when the {speaker} asks: '{utterance}' "

            else:
                summary += f"the {speaker} says: '{utterance}'. "

        return summary

    def get_speaker(self, line):
        if ":" not in line:
            return None

        return line.split(":")[0]

    def get_utterance(self, line):
        if ":" not in line:
            return None

        return line.split(":")[1]

    def get_context_for_facts(self, text):
        return f"The bot remembers: '{text}'"

    def get_relevant_query_answer_context(self, text, query_text, answer):
        if "the user says:" in text.lower():
            return f"when asked '{query_text}' the user says '{answer}'"

        if "the bot says:" in text.lower():
            return f"when asked '{query_text}' the bot says '{answer}'"

        if "the bot remembers:" in text.lower():
            return f"when asked '{query_text}' the bot says '{answer}'"

        return f"the answer to '{query_text}' is '{answer}'"
