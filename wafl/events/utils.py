from wafl.simple_text_processing.normalize import normalized


def input_is_valid(text):
    if not text.strip():
        return False

    if normalized(text) != "no" and len(text) <= 2:
        return False

    return True
