import os
import joblib
import numpy as np


from wafl.qa.qa import get_perplexity


_path = os.path.dirname(__file__)

### Refactor this to "model/" folder
_cv = joblib.load(
    os.path.join(_path, "/home/alce/src/wafl/models/discourse_count_vectorizer.joblib")
)


def _get_text_from_prompt(prompt):
    return f"""
In the text below two people are discussing a story.

Story:
The user asks a few questions.

Discussion:
Q:{prompt}
""".strip()


def choose_best_output(sentences):
    best_sentence = sentences[0][0]
    null_hypothesis = ("", -3.5, -3.5)
    best_score = 1e6

    for sentence in list(sentences) + [null_hypothesis]:
        prompt = sentence[0]
        if not prompt:
            continue

        original_score = sentence[-2]
        score = get_perplexity(_get_text_from_prompt(prompt)) - 1.5 * original_score

        score -= np.sum(_cv.transform([prompt]).toarray())

        if score < best_score:
            best_score = score
            best_sentence = sentence[0]

    return best_sentence
