from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.events.events_from_module_name import EventsCreatorFromModuleName
from wafl.events.generated_events import GeneratedEvents
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge
from wafl.run import _logger
from wafl.scheduler.conversation_loop import ConversationLoop
from wafl.scheduler.generated_event_loop import GeneratedEventLoop
from wafl.scheduler.scheduler import Scheduler


def run_from_audio():
    config = Configuration.load_local_config()
    knowledge = ProjectKnowledge("rules.wafl", logger=_logger)
    interface = VoiceInterface(config)
    conversation_events = ConversationEvents(
        knowledge,
        interface=interface,
        code_path=knowledge.get_dependencies_list(),
        config=config,
        logger=_logger,
    )
    conversation_loop = ConversationLoop(
        interface,
        conversation_events,
        _logger,
        activation_word=config.get_value("waking_up_word"),
    )
    generated_events = GeneratedEvents(
        knowledge,
        events=EventsCreatorFromModuleName("events"),
        interface=interface,
    )
    events_loop = GeneratedEventLoop(
        interface,
        generated_events,
        logger=_logger,
    )
    scheduler = Scheduler([conversation_loop, events_loop])
    scheduler.run()