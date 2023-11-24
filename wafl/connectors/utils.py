def select_best_answer(answers):
    special_words = ["</remember>", "</execute>"]
    return sorted(answers, key=lambda x: sum([x.count(word) for word in special_words]))[-1]