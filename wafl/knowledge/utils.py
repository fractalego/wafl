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
