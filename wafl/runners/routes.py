import os

from flask import Flask
from flask_cors import CORS

_path = os.path.dirname(__file__)
app = Flask(
    __name__,
    static_url_path="",
    static_folder=os.path.join(_path, "../frontend/"),
    template_folder=os.path.join(_path, "../frontend/"),
)
CORS(app)


def get_app():
    return app


def add_new_rules(app: Flask, conversation_id: int, web_server_loop: "WebLoop"):
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
    app.add_url_rule(
        f"/{conversation_id}/toggle_logs",
        f"toggle_logs_{conversation_id}",
        web_server_loop.toggle_logs,
        methods=["POST"],
    )
