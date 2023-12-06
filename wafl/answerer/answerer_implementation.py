def get_last_bot_utterance(dialogue_items):
    for item in reversed(dialogue_items):
        if item[1].startswith("bot:"):
            return item[1].replace("bot:", "").strip()

    return ""


def get_last_user_utterance(dialogue_items):
    for item in reversed(dialogue_items):
        if item[1].startswith("user:"):
            return item[1].replace("user:", "").strip()

    return ""