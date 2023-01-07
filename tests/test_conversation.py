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


class TestConversation(TestCase):
    def test__single_utterance(self):
        interface = DummyInterface()
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
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
        assert interface.get_utterances_list()[-1] == expected

    def test_input_during_inference(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        input_from_user = "Can I register to the newsletter?".capitalize()
        asyncio.run(conversation_events._process_query(input_from_user))
        expected = "bot: Test@example.com has been added to the newsletter"
        assert interface.get_utterances_list()[-1] == expected

    def test__remember_command(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        input_from_user = "Can I register to the newsletter?".capitalize()
        asyncio.run(conversation_events._process_query(input_from_user))
        answer = asyncio.run(
            conversation_events._process_query("What is the email of the user")
        )
        assert answer.text == "test@example.com"

    def test__knowledge_insertion(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        input_from_user = "the user's mother is called Ada"
        asyncio.run(conversation_events._process_query(input_from_user))
        answer = asyncio.run(
            conversation_events._process_query("How is the user's mum called")
        )
        print(answer)
        assert answer.text.lower() == "ada"

    def test__greeting(self):
        interface = DummyInterface(["My name is Albert", "What is my name"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        assert interface.get_utterances_list()[-1].lower() == "bot: albert"

    def test__greeting_with_alberto_as_name(self):
        interface = DummyInterface(["My name is Albert0", "What is my name"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        assert interface.get_utterances_list()[-1].lower() == "bot: albert0"

    def test__yes(self):
        interface = DummyInterface(["My name is Ada", "am I called Ada"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        assert "yes" in interface.get_utterances_list()[-1].lower()

    def test__no(self):
        interface = DummyInterface(["My name is Albert", "Is my name Bob"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        assert "no" in interface.get_utterances_list()[-1].lower()

    def test__yes_no_questions_from_bot_with_answer_yes(self):
        interface = DummyInterface(["I want to join the club", "yes"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
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
        interface.output(utterance)
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
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        assert interface.get_utterances_list()[-1] == "bot: Nice to meet you, albert!"

    def test__conversation_input_returns_false_for_trivial_input(self):
        interface = DummyInterface(["uhm what"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge("", logger=_logger), interface=interface, logger=_logger
        )
        result = asyncio.run(conversation_events.process_next())
        assert not result

    def test__how_are_you(self):
        interface = DummyInterface(["How are you?"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_how_are_you, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        assert "doing well" in interface.get_utterances_list()[-1]
