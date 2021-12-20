from wafl.facts import Fact
from wafl.rules import Rule


def get_facts_and_rules_from_text(text: str):
    lines = _get_lines_stripped_from_comments(text)

    facts = []
    rules = []

    rule_length = 0
    effect = ''
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
            causes.append(Fact(text=line.strip()))

        else:
            if '?' in line:
                is_question = True
                variable = line.split('?')[1].strip()
            else:
                is_question = False
                variable = None
            effect = Fact(text=line.strip(), is_question=is_question, variable=variable)

    return {'facts': facts, 'rules': rules}


def _get_lines_stripped_from_comments(text):
    lines = []
    for line in text.split('\n'):
        if line.strip() and line.strip()[0] == '#':
            continue

        line = line.split('#')[0]
        lines.append(line)

    lines.append('')
    return lines
