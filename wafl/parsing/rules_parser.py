from wafl.conversation.utils import is_question
from wafl.facts import Fact
from wafl.parsing.utils import get_lines_stripped_from_comments, is_quoted_text
from wafl.rules import Rule


def get_facts_and_rules_from_text(text: str):
    lines = get_lines_stripped_from_comments(text)

    facts = []
    rules = []

    rule_length = 0
    effect = ""
    causes = []

    for line in lines:
        if not line.strip():
            if not effect:
                continue

            if rule_length == 0:
                facts.append(effect)

            else:
                rules.append(Rule(effect=effect, causes=causes))

            effect = None
            causes = []
            rule_length = 0

        separation = line.find(line.strip())
        if separation > 0:
            rule_length += 1
            text = line.strip()
            causes.append(Fact(text=text, is_question=is_question(text)))

        else:
            if "=" in line:
                sentence_is_question = True
                variable, text = line.split("=")
                text = text.strip()
                variable = variable.strip()

            else:
                sentence_is_question = False
                variable = None
                text = line.strip()
                if is_quoted_text(text):
                    text += "The user says: " + text

            effect = Fact(
                text=text, is_question=sentence_is_question, variable=variable
            )

    return {"facts": facts, "rules": rules}
