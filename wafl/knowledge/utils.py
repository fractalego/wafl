from wafl.retriever.dense_retriever import get_dot_product


def text_is_exact_string(text):
    return text.strip() and text.strip()[0] == "_"


def items_are_too_different(items):
    dot_products = []
    for item in items[1:]:
        dot_products.append(get_dot_product(item.effect.text, items[0].effect.text))
        print("DOT PRODUCT:", get_dot_product(item.effect.text, items[0].effect.text))

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
