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
