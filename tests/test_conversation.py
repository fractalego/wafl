import asyncio

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.logger.local_file_logger import LocalFileLogger

_logger = LocalFileLogger()

_wafl_example = """

The user greets
  username = What is the user's name
  SAY hello to you, {username}!

The user says they can swim
  username = What is the user's name
  the user is called {username}

color = What is the user's hair color
  username = What is the user's name
  {username} has {color} hair

the user wants to register to the newsletter
  email = what is the user's email
  REMEMBER the user's email is {email}
  SAY {email} has been added to the newsletter

This bot name is Fractalego

the user is very happy

The user's name is Bob

Bob has black hair

""".strip()

_wafl_greetings = """
The user greets
  SAY Hello there!
  username = What is the user's name
  REMEMBER the user is called {username}
  REMEMBER the user's name is {username}
  SAY Nice to meet you, {username}!
  
The user wants to join the club
  Is the user good enough to join?
  SAY Welcome to the club!

""".strip()

_wafl_how_are_you = """

This bot name is Computer
This bot is doing well

""".strip()


_wafl_dialogue_variable = """

The user wants this bot to say something about the user
    reply = Given this dialogue {_dialogue} say something about the user
    SAY {reply}

""".strip()


class TestConversation(TestCase):
    def test__single_utterance(self):
        interface = DummyInterface()
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        assert interface.get_utterances_list()[0] == "bot: " + utterance

    def test__say_command(self):
        interface = DummyInterface()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        input_from_user = "hello!".capitalize()
        asyncio.run(conversation_events._process_query(input_from_user))
        expected = "bot: Hello to you, bob!"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected

    def test_input_during_inference(self):
        interface = DummyInterface(
            to_utter=["Can I register to the newsletter?", "test@example.com"]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Test@example.com has been added to the newsletter"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected

    def test__remember_command(self):
        interface = DummyInterface(
            to_utter=[
                "Can I register to the newsletter?",
                "test@example.com",
                "What is the email of the user",
            ]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "test@example.com"
        print(interface.get_utterances_list())
        assert expected in interface.get_utterances_list()[-1].lower()

    def test__knowledge_insertion(self):
        interface = DummyInterface(
            to_utter=["the user's mother is called Ada", "How is the user's mum called"]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "ada"
        print(interface.get_utterances_list())
        assert expected in interface.get_utterances_list()[-1].lower()

    def test__greeting(self):
        interface = DummyInterface(["My name is Albert", "What is my name"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge("", logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "albert"
        assert expected in interface.get_utterances_list()[-1].lower()

    def test__greeting_with_alberto_as_name(self):
        interface = DummyInterface(["My name is Albert0", "What is my name"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "albert0"
        print(interface.get_utterances_list())
        assert expected in interface.get_utterances_list()[-1].lower()

    def test__yes(self):
        interface = DummyInterface(["My name is Ada", "am I called Ada"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        assert (
            "yes" in interface.get_utterances_list()[-1].lower()
            or "ada" in interface.get_utterances_list()[-1].lower()
        )

    def test__no(self):
        interface = DummyInterface(["My name is Albert", "Is my name Bob?"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        assert (
            "no" in interface.get_utterances_list()[-1].lower()
            or "albert" in interface.get_utterances_list()[-1].lower()
        )

    def test__yes_no_questions_from_bot_with_answer_yes(self):
        interface = DummyInterface(["I want to join the club", "yes"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        asyncio.run(conversation_events.process_next())
        assert interface.get_utterances_list()[-1] == "bot: Welcome to the club!"

    def test__yes_no_questions_from_bot_with_answer_no(self):
        interface = DummyInterface(["I want to join the club", "no"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        asyncio.run(conversation_events.process_next())
        assert (
            interface.get_utterances_list()[-2] == "bot: are you good enough to join?"
        )

    def test__hello_and_username(self):
        interface = DummyInterface(["Hello", "Albert"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == "bot: Nice to meet you, albert!"

    def test__how_are_you(self):
        interface = DummyInterface(["How are you?"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_how_are_you, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        assert "doing well" in interface.get_utterances_list()[-1]

    def test__dialogue_variable_works(self):
        interface = DummyInterface(
            ["my name is Albert0 and I am a carpenter", "say something about me"]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_dialogue_variable, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "albert0"
        print(interface.get_utterances_list())
        assert expected in interface.get_utterances_list()[-1].lower()
