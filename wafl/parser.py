from wafl.facts import Fact
from wafl.rules import Rule


def get_facts_and_rules_from_text(text: str):
    lines = []
    for line in text.split('\n'):
        if line.strip() and line.strip()[0] == '#':
            continue

        line = line.split('#')[0]
        lines.append(line)
    lines.append('')

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
                facts.append(Fact(text=effect))

            else:
                rules.append(Rule(effect=effect, causes=causes))

            effect = ''
            causes = []
            rule_length = 0

        separation = line.find(line.strip())
        if separation > 0:
            rule_length += 1
            causes.append(line.strip())

        else:
            effect = line.strip()

    return {'facts': facts, 'rules': rules}
