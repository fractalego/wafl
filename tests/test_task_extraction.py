import asyncio

from unittest import TestCase
from wafl.extractors.task_extractor import TaskExtractor
from wafl.interface.dummy_interface import DummyInterface


class TestTaskMemory(TestCase):
    def test__query_extractor(self):
        interface = DummyInterface()
        task_extractor = TaskExtractor(interface)
        prediction = asyncio.run(task_extractor.extract("hello what time is it")).text
        expected = "the user asks what time it is"
        assert expected == prediction

    def test__dialogue_extractor1(self):
        interface = DummyInterface()
        interface._utterances = [
            [0, "user: hello what time is it"],
        ]
        task_extractor = TaskExtractor(interface)
        prediction = asyncio.run(task_extractor.extract("")).text
        expected = "the user says hello AND asks what time it is"
        assert expected == prediction

    def test__dialogue_extractor2(self):
        interface = DummyInterface()
        interface._utterances = [
            [0, "user: hello what time is it"],
            [1, "bot: hello there"],
            [2, "bot: The time is 20 past 13"],
            [3, "user: what is in the shopping list"],
        ]
        task_extractor = TaskExtractor(interface)
        prediction = asyncio.run(task_extractor.extract("")).text
        expected = "the user wants to know what is in the shopping list"
        assert expected == prediction

    def test__dialogue_extractor3(self):
        interface = DummyInterface()
        interface._utterances = [
            [0, "user: hello what time is it"],
            [1, "bot: hello there"],
            [2, "bot: The time is 20 past 13"],
            [3, "user: what is in the shopping list"],
            [4, "bot: the shopping list contains milk, bread, and eggs"],
            [4, "user: what about the jubilee line"],
        ]
        task_extractor = TaskExtractor(interface)
        prediction = asyncio.run(task_extractor.extract("")).text
        expected = "the user wants to know about the jubilee line"
        assert expected == prediction
