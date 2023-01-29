def get_lines_stripped_from_comments(text):
    if not text:
        return []

    lines = []
    for line in text.split("\n"):
        if line.strip() and line.strip()[0] == "#":
            continue

        line = line.split("#")[0]
        lines.append(line)

    lines.append("")
    return lines


def is_quoted_text(text):
    if not text:
        return False

    if text[0] == '"' and text[-1] == '"':
        return True

    return False


def text_has_interruption(text):
    interruption_text = "INTERRUPTION"
    if text.find(interruption_text) == 0:
        return True

    return False


def clean_text(text):
    return text.replace("INTERRUPTION ", "")


def concatenate_slashes_into_one_single_line(text):
    text = text.replace("\\n", "")
    return text
