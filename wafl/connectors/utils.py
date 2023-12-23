def select_best_answer(answers, last_strings):
    special_words = (
        last_strings
        + ["</remember>", "</execute>", "result ="]
        + ["<execute>", "<remember>", "<execute>", "<remember>"]
    )
    return sorted(
        answers, key=lambda x: sum([x.count(word) for word in special_words])
    )[-1]
