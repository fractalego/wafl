def get_html_from_dialogue_item(
    text,
):
    if text.find("bot:") == 0:
            return (
                f"<div class='shadow-lg dialogue-row-bot' style='font-size:20px; '"
                f">" + text[4:].strip() + "</div>"
            )

    return (
        "<div class='dialogue-row-comment' style='font-size:20px; '>"
        + text[5:].strip()
        + "</div>"
    )