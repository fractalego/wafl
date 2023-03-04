from wafl.simple_text_processing.questions import is_question


class Narrator:
    def __init__(self, interface):
        self._interface = interface

    def summarize_dialogue(self):
        dialogue_list = self._interface.get_utterances_list()[-7:]
        summary = ""
        for line in dialogue_list:
            speaker = self.get_speaker(line)
            utterance = self.get_utterance(line)
            if not speaker or not utterance:
                continue

            if is_question(utterance):
                summary += f"when the {speaker} asks: '{utterance}' "

            else:
                summary += f"the {speaker} says: '{utterance}'; "

        summary = self._clean_summary(summary)
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
        text = text.strip()
        return f"The bot remembers: '{text}'"

    def get_relevant_query_answer_context(self, text, query_text, answer):
        if "the user says:" in text.lower():
            return f"when asked: '{query_text}' the user says '{answer}'"

        if "the bot says:" in text.lower():
            return f"when asked: '{query_text}' the bot says '{answer}'"

        if "the bot remembers:" in text.lower():
            return f"when asked: '{query_text}' the bot remembers '{answer}'"

        return f"the answer to '{query_text}' is '{answer}'"

    def get_relevant_fact_context(self, text, answer):
        text = text.strip()
        answer = answer.strip()
        if "the user says:" in text.lower():
            return f"the user says '{answer}'"

        if "the bot says:" in text.lower():
            return f"the bot says '{answer}'"

        if "the bot remembers:" in text.lower():
            return f"the bot remembers '{answer}'"

        return answer

    def _clean_summary(self, text):
        text = text.replace(";.", ";")
        return text
