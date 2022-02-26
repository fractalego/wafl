from wafl.inference.utils import project_answer, normalized

from wafl.conversation.utils import is_question
from wafl.facts import Fact
from wafl.parsing.utils import (
    get_lines_stripped_from_comments,
    is_quoted_text,
    text_has_interruption,
    clean_text,
)
from wafl.qa.qa import QA, Query
from wafl.rules import Rule

_qa = QA()


def get_source_from_text(text, default):
    answer = _qa.ask(query=Query(text="who is speaking?", is_question=True), text=text)
    if normalized(answer.text) == "unknown":
        return default

    return project_answer(answer, ["user", "bot"])


def get_destination_from_text(text, speaker, default):
    answer = _qa.ask(
        query=Query(text=f"who is {speaker} speaking to?", is_question=True), text=text
    )
    if normalized(answer.text) == "unknown":
        return default

    return project_answer(answer, ["user", "bot"])


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
            source = get_source_from_text(text, default="bot")
            destination = get_destination_from_text(text, source, default="user")

            causes.append(
                Fact(
                    text=text,
                    is_question=is_question(text),
                    source=source,
                    destination=destination,
                )
            )

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
                    text = "The user says: " + text

            is_interruption = text_has_interruption(text)
            if is_interruption:
                text = clean_text(text)

            source = get_source_from_text(text, default="user")
            destination = get_destination_from_text(text, source, default="bot")

            effect = Fact(
                text=text,
                is_question=sentence_is_question,
                variable=variable,
                is_interruption=is_interruption,
                source=source,
                destination=destination,
            )

    return {"facts": facts, "rules": rules}
