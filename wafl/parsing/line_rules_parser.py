from wafl.simple_text_processing.questions import is_question
from wafl.facts import Fact
from wafl.rules import Rule


def parse_rule_from_single_line(text, knowledge_name=None):
    if ":-" not in text:
        return None

    text = text.strip()
    effect_text, causes_text = text.split(":-")
    effect = Fact(
        text=effect_text.strip(),
        is_question=is_question(effect_text),
        knowledge_name=knowledge_name,
    )
    causes = [
        Fact(
            text=item.strip(),
            is_question=is_question(item),
            knowledge_name=knowledge_name,
        )
        for item in causes_text.split(";")
    ]

    return Rule(effect=effect, causes=causes)
