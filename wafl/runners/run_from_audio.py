from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.events.events_from_module_name import EventsCreatorFromModuleName
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.scheduler.conversation_loop import ConversationLoop
from wafl.scheduler.generated_event_loop import GeneratedEventLoop
from wafl.scheduler.scheduler import Scheduler

_logger = LocalFileLogger()


def run_from_audio():
    config = Configuration.load_local_config()
    knowledge = SingleFileKnowledge(
        config, open(config.get_value("rules")).read(), logger=_logger
    )
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
    scheduler = Scheduler([conversation_loop])
    scheduler.run()


if __name__ == "__main__":
    run_from_audio()
