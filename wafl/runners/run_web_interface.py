import asyncio

from wafl.events.conversation_events import ConversationEvents
from wafl.interface.queue_interface import QueueInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.scheduler.conversation_loop import ConversationLoop
from wafl.scheduler.scheduler import Scheduler
from wafl.scheduler.web_loop import WebLoop

_logger = LocalFileLogger()


def run_server():
    interface = QueueInterface()
    knowledge = ProjectKnowledge("rules.wafl", logger=_logger)
    interface.activate()
    conversation_events = ConversationEvents(
        knowledge,
        interface=interface,
        code_path=knowledge.get_dependencies_list(),
        logger=_logger,
    )
    conversation_loop = ConversationLoop(
        interface,
        conversation_events,
        _logger,
        activation_word="",
        max_misses=-1,
    )
    interface.output("Hello. How may I help you?")
    web_loop = WebLoop(interface)
    scheduler = Scheduler([conversation_loop, web_loop])
    asyncio.run(scheduler.run())
