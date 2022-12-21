from wafl.conversation.utils import is_question
from wafl.deixis import from_user_to_bot
from wafl.facts import Fact
from wafl.parsing.utils import (
    get_lines_stripped_from_comments,
    is_quoted_text,
    text_has_interruption,
    clean_text,
)
from wafl.rules import Rule


def get_facts_and_rules_from_text(text: str):
    lines = get_lines_stripped_from_comments(text)
    lines.extend(["LAST"])

    facts = []
    rules = []

    rule_length = 0
    current_fact = ""
    causes = []
    for line in lines:
        separation = line.find(line.strip())
        if separation > 0:
            rule_length += 1
            text = line.strip()
            causes.append(
                Fact(
                    text=text,
                    is_question=is_question(text),
                )
            )

        else:
            text = line.strip()
            if not text:
                continue

            if current_fact:
                if rule_length == 0:
                    facts.append(current_fact)

                else:
                    rules.append(Rule(effect=current_fact, causes=causes))

                causes = []
                rule_length = 0

            if "=" in text:
                sentence_is_question = True
                variable, text = text.split("=")
                text = text.strip()
                variable = variable.strip()

            else:
                sentence_is_question = False
                variable = None
                if is_quoted_text(text):
                    text = "The user says: " + from_user_to_bot(text)

            is_interruption = text_has_interruption(text)
            if is_interruption:
                text = clean_text(text)

            current_fact = Fact(
                text=from_user_to_bot(text),
                is_question=sentence_is_question,
                variable=variable,
                is_interruption=is_interruption,
            )

    return {"facts": facts, "rules": rules}
