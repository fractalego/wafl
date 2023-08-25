from unittest import TestCase

from wafl.simple_text_processing.deixis import from_user_to_bot, from_bot_to_user


class TestDeixis(TestCase):
    def test_from_user_to_bot(self):
        translation = from_user_to_bot("You are called computer")
        expected = "this bot is called computer"
        assert translation == expected

    def test_from_bot_to_user(self):
        translation = from_bot_to_user("The user is Bob")
        expected = "you are Bob"
        assert translation == expected
