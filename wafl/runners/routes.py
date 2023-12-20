import asyncio
import os
import random
import sys
import threading

from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.queue_interface import QueueInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.scheduler.conversation_loop import ConversationLoop
from wafl.scheduler.scheduler import Scheduler
from wafl.scheduler.web_loop import WebLoop

_path = os.path.dirname(__file__)
_logger = LocalFileLogger()
app = Flask(
    __name__,
    static_url_path="",
    static_folder=os.path.join(_path, "../frontend/"),
    template_folder=os.path.join(_path, "../frontend/"),
)
CORS(app)


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


def get_app():
    return app


def create_scheduler_and_webserver_loop(conversation_id):
    config = Configuration.load_local_config()
    interface = QueueInterface()
    interface.activate()
    conversation_events = ConversationEvents(
        config=config,
        interface=interface,
        logger=_logger,
    )
    conversation_loop = ConversationLoop(
        interface,
        conversation_events,
        _logger,
        activation_word="",
        max_misses=-1,
        deactivate_on_closed_conversation=False,
    )
    asyncio.run(interface.output("Hello. How may I help you?"))
    web_loop = WebLoop(interface, conversation_id, conversation_events)
    return {
        "scheduler": Scheduler([conversation_loop, web_loop]),
        "web_server_loop": web_loop,
    }


def add_new_rules(app, conversation_id, web_server_loop):
    app.add_url_rule(
        f"/{conversation_id}/",
        f"index_{conversation_id}",
        web_server_loop.index,
        methods=["GET"],
    )
    app.add_url_rule(
        f"/{conversation_id}/reset_conversation",
        f"reset_conversation_{conversation_id}",
        web_server_loop.reset_conversation,
        methods=["POST"],
    )
    app.add_url_rule(
        f"/{conversation_id}/reload_rules",
        f"reload_rules_{conversation_id}",
        web_server_loop.reload_rules,
        methods=["POST"],
    )
    app.add_url_rule(
        f"/{conversation_id}/check_new_messages",
        f"check_new_messages_{conversation_id}",
        web_server_loop.check_for_new_messages,
        methods=["POST"],
    )
    app.add_url_rule(
        f"/{conversation_id}/load_messages",
        f"load_messages_{conversation_id}",
        web_server_loop.load_messages,
        methods=["POST", "GET"],
    )
    app.add_url_rule(
        f"/{conversation_id}/input",
        f"input_{conversation_id}",
        web_server_loop.handle_input,
        methods=["POST", "GET"],
    )
    app.add_url_rule(
        f"/{conversation_id}/output",
        f"output_{conversation_id}",
        web_server_loop.handle_output,
        methods=["POST"],
    )
    app.add_url_rule(
        f"/{conversation_id}/thumbs_up",
        f"thumbs_up_{conversation_id}",
        web_server_loop.thumbs_up,
        methods=["POST"],
    )
    app.add_url_rule(
        f"/{conversation_id}/thumbs_down",
        f"thumbs_down_{conversation_id}",
        web_server_loop.thumbs_down,
        methods=["POST"],
    )
