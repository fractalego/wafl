import os
import joblib
import numpy as np


from wafl.qa.qa import get_perplexity


_path = os.path.dirname(__file__)

### Refactor this to "model/" folder
_cv = joblib.load(
    os.path.join(_path, "/home/alce/src/wafl/models/discourse_count_vectorizer.joblib")
)


def choose_best_output(sentences):
    best_sentence = sentences[0][0]
    best_score = 1e6

    for sentence in sentences[:15]:
        prompt = sentence[0]
        original_score = sentence[-1]
        score = get_perplexity(prompt) - 1.5 * original_score

        score -= np.sum(_cv.transform([prompt]).toarray())

        if score < best_score:
            best_score = score
            best_sentence = sentence[0]

    return best_sentence
