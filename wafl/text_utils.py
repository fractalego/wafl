import re


def clean_text_for_retrieval(text):
    return re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", text)
