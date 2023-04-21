import logging
import os
import threading

from flask import Flask, render_template, request, jsonify, g
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
            conversation = "</br>".join(self._interface.get_utterances_list()) + "</br>"
            conversation += (
                '<script>document.getElementById("query").value = "";</script>'
            )
            return conversation

        @app.route("/load_messages", methods=["GET"])
        async def load_messages():
            conversation = "</br>".join(self._interface.get_utterances_list())
            return conversation

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
