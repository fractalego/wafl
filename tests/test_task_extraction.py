import asyncio

from unittest import TestCase
from wafl.extractors.task_extractor import TaskExtractor
from wafl.interface.dummy_interface import DummyInterface


class TestTaskExtraction(TestCase):
    def test__dialogue_extractor1(self):
        interface = DummyInterface()
        interface._utterances = [
            [0, "user: what time is it"],
        ]
        task_extractor = TaskExtractor(interface)
        prediction = asyncio.run(task_extractor.extract("")).text
        expected = "wants to know the time"
        print(prediction)
        assert expected in prediction

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
            [5, "user: is the circle line running"],
            [6, "bot: yes, it is running normally"],
            [7, "user: what about the Jubilee line"],
        ]
        task_extractor = TaskExtractor(interface)
        prediction = asyncio.run(task_extractor.extract("")).text
        expected = "the user wants to know if the Jubilee line is running"
        print(prediction)
        assert expected == prediction

    def test__no_task_present_is_predicted_as_unknown(self):
        interface = DummyInterface()
        interface._utterances = [
            [0, "user: hello what time is it"],
            [1, "bot: hello there"],
            [2, "bot: The time is 20 past 13"],
            [3, "user: what is in the shopping list"],
            [4, "bot: the shopping list contains milk, bread, and eggs"],
            [5, "user: you"],
        ]
        task_extractor = TaskExtractor(interface)
        prediction = asyncio.run(task_extractor.extract("")).text
        expected = "unknown"
        print(prediction)
        assert expected == prediction
