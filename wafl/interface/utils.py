from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from wafl.simple_text_processing.normalize import normalized


def get_most_common_words(text, max_num_words, count_threshold=1):
    corpus = text.split("\n")
    cv = CountVectorizer(ngram_range=(1, 2))
    words_count = cv.fit_transform(corpus).sum(axis=0)
    words_freq = [
        (word, words_count[0, index])
        for word, index in cv.vocabulary_.items()
        if words_count[0, index] >= count_threshold
        and word not in ENGLISH_STOP_WORDS
        and "user" not in word
        and "bot" not in word
    ]
    words_freq = sorted(words_freq, key=lambda x: -x[1])
    return [word for word, _ in words_freq][:max_num_words]


def not_good_enough(text):
    if not text:
        return True

    if "[unclear]" in text:
        return True

    if normalized(text) != "no" and len(text.strip().replace(" ", "")) < 3:
        return True

    return False
