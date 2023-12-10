def get_last_bot_utterances(dialogue_items, num_utterances):
    utterances = []
    for item in reversed(dialogue_items):
        if item[1].startswith("bot:"):
            utterances.append(item[1].replace("bot:", "").strip())

        if len(utterances) == num_utterances:
            break

    return utterances


def get_last_user_utterance(dialogue_items):
    for item in reversed(dialogue_items):
        if item[1].startswith("user:"):
            return item[1].replace("user:", "").strip()

    return ""
