def normalized(text, lower_case=True):
    text = text.strip()
    if not text:
        return ""

    if text[-1] == ".":
        text = text[:-1]

    if lower_case:
        text = text.lower()

    return text.strip()
