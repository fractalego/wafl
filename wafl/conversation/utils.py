def is_question(text):
    text = text.strip()
    if text[-1] == "?":
        return True

    first_word = text.split()
    if first_word in [
        "what",
        "who",
        "when",
        "where",
        "how",
        "can",
        "may",
    ]:  ### NOT GOOD ENOUGH
        return True

    return False
