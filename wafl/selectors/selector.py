class Selector:
    _important_strings = [
        "\nuser",
        "\nbot",
        "<|EOS|>",
        "</remember>",
        "</execute>\n",
        "</s>",
    ]
    _special_words = (
            _important_strings
            + ["</remember>", "</execute>", "result ="]
            + ["<execute>", "<remember>", "<execute>", "<remember>"]
    )

    def select_best_answer(self, answers):
        return sorted(
            answers, key=lambda x: sum([x.count(word) for word in self._special_words])
        )[-1]
