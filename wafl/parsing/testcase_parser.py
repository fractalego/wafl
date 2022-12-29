from wafl.parsing.utils import get_lines_stripped_from_comments

_user_prompt = "user:"
_bot_prompt = "bot:"


def get_user_and_bot_lines_from_text(text: str):
    lines = get_lines_stripped_from_comments(text)

    testcase_name = ""
    testcases = {}
    to_negate = False
    bot_lines = []
    user_lines = []
    all_lines = []

    for line in lines:
        if not line.strip():
            continue

        separation = line.find(line.strip())
        if separation == 0:
            if user_lines or bot_lines:
                testcases[testcase_name] = {
                    "bot_lines": bot_lines,
                    "user_lines": user_lines,
                    "lines": all_lines,
                    "negated": to_negate,
                }
                to_negate = False
                bot_lines = []
                user_lines = []
                all_lines = []

            line = line.strip()
            if line.find("!") == 0:
                to_negate = True
                line = line[1:].strip()

            testcase_name = line
            testcases[testcase_name] = {}
            continue

        line = line.strip()
        all_lines.append(line)

        if line.find(_user_prompt) == 0:
            user_lines.append(line[len(_user_prompt) :].strip())
            continue

        if line.find(_bot_prompt) == 0:
            bot_lines.append(line[len(_bot_prompt) :].strip())
            continue

    if user_lines or bot_lines:
        testcases[testcase_name] = {
            "bot_lines": bot_lines,
            "user_lines": user_lines,
            "lines": all_lines,
            "negated": to_negate,
        }

    return testcases
