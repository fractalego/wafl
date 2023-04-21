import wafl.simple_text_processing.questions
from wafl.simple_text_processing.questions import get_sentence_from_yn_question


def text_is_exact_string(text):
    return text.strip() and text.strip()[0] == "_"


def rules_are_too_different(retriever, rules):
    dot_products = []
    for item in rules[1:]:
        dot_products.append(
            retriever.get_dot_product(item.effect.text, rules[0].effect.text)
        )

    if dot_products and min(dot_products) < 0.39:
        return False


def get_first_cluster_of_rules(rules_and_threshold):
    if not rules_and_threshold:
        return []

    _cluster_margin = 0.1

    last_threshold = rules_and_threshold[0][1]
    rules = []
    for rule, threshold in rules_and_threshold:
        if abs(threshold - last_threshold) < _cluster_margin:
            rules.append(rule)

        else:
            break

    return rules


def filter_out_rules_that_are_too_dissimilar_to_query(query, rules_and_scores):
    num_query_words = len(query.text.split())
    new_rules_and_scores = []
    for item in rules_and_scores:
        rule = item[0]
        num_rule_effect_words = len(rule.effect.text.split())
        if num_query_words < num_rule_effect_words / 3:
            continue

        new_rules_and_scores.append(item)

    return new_rules_and_scores


async def filter_out_rules_through_entailment(entailer, query, rules_and_scores):
    new_rules_and_scores = []
    for rule, score in rules_and_scores:
        if rule.effect.is_question:
            new_rules_and_scores.append((rule, score))

        elif needs_substitutions(rule.effect):
            new_rules_and_scores.append((rule, score))

        else:
            entailment_score = await entailer.entails(
                query.text, rule.effect.text, return_threshold=True
            )
            if entailment_score:
                new_rules_and_scores.append((rule, score * entailment_score))
                continue

            entailment_score = await entailer.entails(
                rule.effect.text, query.text, return_threshold=True
            )
            if entailment_score:
                new_rules_and_scores.append((rule, score * entailment_score))

    return sorted(new_rules_and_scores, key=lambda x: -x[1])


def needs_substitutions(effect):
    if any(item in effect.text for item in ["{", "}"]):
        return True

    return False
