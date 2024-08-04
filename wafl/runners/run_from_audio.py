import asyncio

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.indexing_implementation import load_knowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.handlers.conversation_handler import ConversationHandler
from wafl.scheduler.scheduler import Scheduler

_logger = LocalFileLogger()


def run_from_audio():
    config = Configuration.load_local_config()
    asyncio.run(load_knowledge(config, _logger))
    interface = VoiceInterface(config)
    conversation_events = ConversationEvents(
        config=config,
        interface=interface,
        logger=_logger,
    )
    conversation_loop = ConversationHandler(
        interface,
        conversation_events,
        _logger,
        activation_word=config.get_value("waking_up_word"),
    )
    scheduler = Scheduler([conversation_loop])
    scheduler.run()


if __name__ == "__main__":
    run_from_audio()
