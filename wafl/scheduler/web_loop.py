import asyncio
import logging
import os
import threading

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from wafl.interface.queue_interface import QueueInterface
from wafl.logger.history_logger import HistoryLogger

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
    def __init__(self, interface: QueueInterface, knowledge: "ProjectKnowledge"):
        self._interface = interface
        self._knowledge = knowledge
        self._rules_filename = knowledge.rules_filename
        self._hystory_logger = HistoryLogger(self._interface)

    async def run(self):
        @app.route("/input", methods=["POST"])
        async def handle_input():
            query = request.form["query"]
            self._interface.input_queue.append(query)
            return f"""
<input autofocus name="query" id="query" class="input" type="text" placeholder="{query}"
               data-hx-post="/input"
               hx-swap="outerHTML"
               hx-trigger="keyup[keyCode==13]">
<div data-hx-post="/load_messages"
         hx-swap="innerHTML"
         hx-target="#messages"
         hx-trigger="load"
         style="display:none;"
         >
</div>            
            """.strip()

        @app.route("/reset_conversation", methods=["POST"])
        async def reset_conversation():
            self._interface.reset_history()
            await self._interface.output("Hello. How may I help you?")
            conversation = await self._get_conversation()
            return conversation

        @app.route("/reload_rules", methods=["POST"])
        async def reload_rules():
            async with asyncio.Lock():
                self._knowledge.reload_rules(self._rules_filename)
                await self._knowledge.reinitialize_all_retrievers()
                print("Rules reloaded")

            return ""

        @app.route("/load_messages", methods=["POST"])
        async def load_messages():
            conversation = await self._get_conversation()
            return conversation

        @app.route("/output")
        async def handle_output():
            if not self._interface.output_queue:
                return jsonify({"text": "", "silent": False})

            output = self._interface.output_queue.pop(0)
            return jsonify(output)

        @app.route("/thumbs_up", methods=["POST"])
        async def thumbs_up():
            self._hystory_logger.write("thumbs_up")
            return jsonify("")

        @app.route("/thumbs_down", methods=["POST"])
        async def thumbs_down():
            self._hystory_logger.write("thumbs_down")
            return jsonify("")

        @app.route("/")
        async def index():
            return render_template("index.html")

        def run_app():
            app.run(host="0.0.0.0", port=8889)

        thread = threading.Thread(target=run_app)
        thread.start()

    async def _get_conversation(self):
        dialogue = self._interface.get_utterances_list_with_timestamp()
        dialogue = [
            (
                item[0],
                "<div class='dialogue-row' style='font-size:20px; '>"
                + item[1]
                + "</div>",
            )
            for item in dialogue
        ]
        choices = self._interface.get_choices_and_timestamp()
        choices = [
            (
                item[0],
                "<div class='log-row' style='font-size:11px; margin-left=30px;margin-top=10px;color:#2a2a2a;'>"
                + item[1]
                + "</div>",
            )
            for item in choices
        ]
        facts = self._interface.get_facts_and_timestamp()
        facts = [
            (
                item[0],
                "<div class='log-row' style='font-size:11px; margin-left=30px;margin-top=10px;color:#2a2a2a;'>"
                + item[1]
                + "</div>",
            )
            for item in facts
        ]
        choices_and_facts = choices + facts
        choices_and_facts = sorted(choices_and_facts, key=lambda x: x[0])[::-1]
        choices_and_facts = [item[1] for item in choices_and_facts]
        dialogue_items = dialogue
        dialogue_items = sorted(dialogue_items, key=lambda x: x[0])[::-1]
        dialogue_items = [item[1] for item in dialogue_items]
        conversation = "<div id='dialogue' class='dialogue shadow-lg overflow-y-scroll rounded-lg' style='flex-direction: column-reverse;'>"
        conversation += "".join(dialogue_items)
        conversation += "</div>"
        conversation += "<div id='logs' class='logs shadow-lg overflow-y-scroll rounded-lg' style='flex-direction: column-reverse;'>"
        conversation += "".join(choices_and_facts)
        conversation += "</div>"
        return conversation
