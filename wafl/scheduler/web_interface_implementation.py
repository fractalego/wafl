import re


def _change_code_wrapper(text):
    pattern = r"```.*?\n(.*?)```"
    num_rows = text.count("\n") - 1

    def replace_code(match):
        code = match.group(1)
        return f'<textarea readonly id="code" rows="{num_rows}">{code}</textarea>'

    return re.sub(pattern, replace_code, text, flags=re.DOTALL)


def get_html_from_dialogue_item(
    text,
):
    if text.find("bot:") == 0:
        return (
            f"<div class='shadow-lg dialogue-row-bot' style='font-size:20px; '"
            f">" + _change_code_wrapper(text[4:]).strip() + "</div>"
        )

    return (
        "<div class='dialogue-row-user' style='font-size:20px; '>"
        + text[5:].strip()
        + "</div>"
    )
