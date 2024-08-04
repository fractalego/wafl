import asyncio
import random
import sys
import threading

from flask import render_template, redirect

from wafl.interface.list_interface import ListInterface
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.indexing_implementation import load_knowledge
from wafl.scheduler.scheduler import Scheduler
from wafl.handlers.conversation_handler import ConversationHandler
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.queue_interface import QueueInterface
from wafl.config import Configuration
from wafl.runners.routes import get_app, add_new_routes
from wafl.handlers.web_handler import WebHandler

app = get_app()
_logger = LocalFileLogger()


@app.route("/create_new_instance", methods=["POST"])
def create_new_web_and_audio_instance():
    conversation_id = random.randint(0, sys.maxsize)
    result = create_web_and_audio_scheduler_and_webserver_loop(conversation_id)
    add_new_routes(conversation_id, result["web_server_handler"])
    thread = threading.Thread(target=result["scheduler"].run)
    thread.start()
    return redirect(f"{conversation_id}/index")


@app.route("/")
async def index_web_and_audio_():
    return render_template("selector.html")


def create_web_and_audio_scheduler_and_webserver_loop(conversation_id):
    config = Configuration.load_local_config()
    interface = ListInterface([VoiceInterface(config), QueueInterface()])
    interface.activate()
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
    web_handler = WebHandler(interface, config, conversation_id, conversation_events)
    return {
        "scheduler": Scheduler([conversation_loop, web_handler]),
        "web_server_handler": web_handler,
    }


def run_app():
    app.run(
        host="0.0.0.0",
        port=Configuration.load_local_config().get_value("frontend_port"),
    )


if __name__ == "__main__":
    run_app()
