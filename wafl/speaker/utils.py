import decimal

from num2words import num2words


def convert_numbers_to_words(text):
    words = text.split()
    new_words = []
    for word in words:
        new_word = word
        try:
            if any(number in word for number in "1234567890"):
                new_word = num2words(word)

        except decimal.InvalidOperation as e:
            pass

        new_words.append(new_word)

    return " ".join(new_words).replace("-", " ")
