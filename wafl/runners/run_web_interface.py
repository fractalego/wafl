import asyncio
import random
import sys
import threading

from flask import render_template, redirect, url_for

from wafl.scheduler.scheduler import Scheduler
from wafl.scheduler.web_handler import WebHandler
from wafl.scheduler.conversation_handler import ConversationHandler
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.queue_interface import QueueInterface
from wafl.config import Configuration
from wafl.runners.routes import get_app, add_new_rules


app = get_app()
_logger = LocalFileLogger()


def run_server_only_app():
    @app.route("/create_new_instance", methods=["POST"])
    def create_new_instance():
        conversation_id = random.randint(0, sys.maxsize)
        result = create_scheduler_and_webserver_loop(conversation_id)
        add_new_rules(app, conversation_id, result["web_server_loop"])
        thread = threading.Thread(target=result["scheduler"].run)
        thread.start()
        return redirect(url_for(f"index_{conversation_id}"))

    @app.route("/")
    async def index():
        return render_template("selector.html")

    def create_scheduler_and_webserver_loop(conversation_id):
        config = Configuration.load_local_config()
        interface = QueueInterface()
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
            activation_word="",
            max_misses=-1,
            deactivate_on_closed_conversation=False,
        )
        asyncio.run(interface.output("Hello. How may I help you?"))
        web_loop = WebHandler(interface, conversation_id, conversation_events)
        return {
            "scheduler": Scheduler([conversation_loop, web_loop]),
            "web_server_loop": web_loop,
        }

    app.run(
        host="0.0.0.0",
        port=Configuration.load_local_config().get_value("frontend_port"),
    )


if __name__ == "__main__":
    run_server_only_app()
