import os

from flask import Flask, abort
from flask_cors import CORS

_path = os.path.dirname(__file__)
app = Flask(
    __name__,
    static_url_path="",
    static_folder=os.path.join(_path, "../frontend/"),
    template_folder=os.path.join(_path, "../frontend/"),
)
CORS(app)

_routes_dict = {}


def get_app():
    return app


@app.route("/<conversation_id>/index", methods=["GET"])
async def get_index(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["index"]()


@app.route("/<conversation_id>/reset_conversation", methods=["POST"])
async def reset_conversation(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["reset_conversation"]()


@app.route("/<conversation_id>/reload_rules", methods=["POST"])
async def reload_rules(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["reload_rules"]()


@app.route("/<conversation_id>/check_new_messages", methods=["POST"])
async def check_new_messages(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["check_new_messages"]()


@app.route("/<conversation_id>/load_messages", methods=["POST", "GET"])
async def load_messages(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["load_messages"]()


@app.route("/<conversation_id>/input", methods=["POST", "GET"])
async def input(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["input"]()


@app.route("/<conversation_id>/output", methods=["POST"])
async def output(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["output"]()


@app.route("/<conversation_id>/thumbs_up", methods=["POST"])
async def thumbs_up(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["thumbs_up"]()


@app.route("/<conversation_id>/thumbs_down", methods=["POST"])
async def thumbs_down(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["thumbs_down"]()


@app.route("/<conversation_id>/toggle_logs", methods=["POST"])
async def toggle_logs(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["toggle_logs"]()


@app.route("/<conversation_id>/get_info", methods=["POST"])
async def get_info(conversation_id: str):
    if conversation_id not in _routes_dict:
        abort(404)
    return await _routes_dict[conversation_id]["get_info"]()


def add_new_routes(conversation_id: str, web_server_handler: "WebHandler"):
    _routes_dict[str(conversation_id)] = {
        "index": web_server_handler.index,
        "reset_conversation": web_server_handler.reset_conversation,
        "reload_rules": web_server_handler.reload_rules,
        "check_new_messages": web_server_handler.check_for_new_messages,
        "load_messages": web_server_handler.load_messages,
        "input": web_server_handler.handle_input,
        "output": web_server_handler.handle_output,
        "thumbs_up": web_server_handler.thumbs_up,
        "thumbs_down": web_server_handler.thumbs_down,
        "toggle_logs": web_server_handler.toggle_logs,
        "get_info": web_server_handler.get_info,
    }
