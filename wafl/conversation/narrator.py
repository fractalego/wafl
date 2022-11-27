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
