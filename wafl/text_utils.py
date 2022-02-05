def clean_text_for_retrieval(text):
    text = text.replace("{", "").replace("}", "")
    return text
