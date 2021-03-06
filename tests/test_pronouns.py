from unittest import TestCase

from wafl.deixis import from_user_to_bot, from_bot_to_user


class TestInference(TestCase):
    def test_from_user_to_bot(self):
        translation = from_user_to_bot("I am Bob")
        expected = "the user is Bob"
        assert translation == expected

    def test_from_bot_to_user(self):
        translation = from_bot_to_user("The user is Bob")
        expected = "you are Bob"
        assert translation == expected
