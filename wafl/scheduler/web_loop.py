import logging
import os
import threading

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from wafl.interface.queue_interface import QueueInterface

_path = os.path.dirname(__file__)
app = Flask(
    __name__,
    static_url_path="",
    static_folder=os.path.join(_path, "../frontend/"),
    template_folder=os.path.join(_path, "../frontend/"),
)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["async_mode"] = "asyncio"
log = logging.getLogger("werkzeug")
log.setLevel(logging.WARNING)


class WebLoop:
    def __init__(self, interface: QueueInterface):
        self._interface = interface

    async def run(self):
        @app.route("/input", methods=["POST"])
        async def handle_input():
            text = request.form["query"]
            self._interface.input_queue.append(text)
            conversation = await self._get_conversation()
            conversation += (
                '<script>document.getElementById("query").value = "";</script>'
            )
            return conversation

        @app.route("/load_messages", methods=["GET"])
        async def load_messages():
            return await self._get_conversation()

        @app.route("/output")
        async def handle_output():
            if not self._interface.output_queue:
                return jsonify({"text": "", "silent": False})

            output = self._interface.output_queue.pop(0)
            return jsonify(output)

        @app.route("/")
        async def index():
            return render_template("index.html")

        def run_app():
            app.run(host="0.0.0.0", port=8889)

        thread = threading.Thread(target=run_app)
        thread.start()

    async def _get_conversation(self):
        dialogue = self._interface.get_utterances_list_with_timestamp()
        dialogue = [(item[0], "<div class='row' style='font-size:30px;'>" + item[1] + "</div>") for item in dialogue]
        choices = self._interface.get_choices_and_timestamp()
        choices = [(item[0], "<div class='row' style='font-size:20px;margin-left=30px;margin-top=10px;color:#fafafa;'>" + item[1] + "</div>") for item in choices]
        facts = self._interface.get_facts_and_timestamp()
        facts = [(item[0], "<div class='row' style='font-size:20px;margin-left=30px;margin-top=10px;color:#fafafa;'>" + item[1] + "</div>") for item in facts]
        dialogue_items = dialogue + choices + facts
        dialogue_items = sorted(dialogue_items, key=lambda x: x[0])
        dialogue_items = [item[1] for item in dialogue_items]
        conversation = "<div class='col'>"
        conversation += "".join(dialogue_items)
        conversation += "</div>"
        return conversation
