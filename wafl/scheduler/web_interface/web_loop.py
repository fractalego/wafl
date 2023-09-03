import asyncio
import logging
import os
import time

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from wafl.interface.queue_interface import QueueInterface
from wafl.logger.history_logger import HistoryLogger

_path = os.path.dirname(__file__)
app = Flask(
    __name__,
    static_url_path="",
    static_folder=os.path.join(_path, "../../frontend/"),
    template_folder=os.path.join(_path, "../../frontend/"),
)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["async_mode"] = "asyncio"
log = logging.getLogger("werkzeug")
log.setLevel(logging.WARNING)


def get_html_from_dialogue_item(text, index, conversation_id, bot_is_computing_answer, reload_messages=False, autofocus=False):
    if text.find("bot:") == 0:
        if bot_is_computing_answer:
            return (
                f"<div id='messages-{index}'"
                f"hx-post='/{conversation_id}/{index}/messages'"
                f"hx-swap='outerHTML'"
                f"hx-target='#messages-{index}'"
                f"hx-trigger='every 1s'"
                f">" + text[4:].strip() + "</div>"
            )

        if reload_messages:
            return (
                f"<div id='messages-{index}' class='shadow-lg dialogue-row-bot' style='font-size:20px; '"
                f"hx-post='/{conversation_id}/load_messages'"
                f"hx-swap='innerHTML'"
                f"hx-target='#messages'"
                f"hx-trigger='load'"
                f">" + text[4:].strip() + "</div>"
            )

        else:
            return (
                    f"<div id='messages-{index}' class='shadow-lg dialogue-row-bot' style='font-size:20px; '"
                    f">" + text[4:].strip() + "</div>"
            )

    if text.find("user:") == 0:
        autofocus_str = "autofocus" if autofocus else ""
        return (
            f"<textarea {autofocus_str} id='textarea-{index}'"
            f"class='shadow-lg dialogue-row-user' name='query' rows='1' style='font-size:20px; min-height:50px;' type='text'"
            f"hx-post='/{conversation_id}/{index}/input'"
            f"hx-swap='outerHTML'"
            f"hx-target='#messages-{index+1}'"
            f"hx-trigger='keydown[!shiftKey&&keyCode==13]'"
            f">" + text[5:] + "</textarea>"
            f"""
<script>
$("#textarea-{index}").on("keydown", function(e){{
  if (e.keyCode == 13 && !e.shiftKey)
  {{
    // prevent default behavior
    e.preventDefault();
    return false;
  }}
}});
</script>
            """
        )

    return (
        "<div class='dialogue-row-comment' style='font-size:20px; '>"
        + text.strip()
        + "</div>"
    )


class WebLoop:
    def __init__(
        self,
        interface: QueueInterface,
        knowledge: "ProjectKnowledge",
        conversation_id: int,
    ):
        self._interface = interface
        self._knowledge = knowledge
        self._rules_filename = knowledge.rules_filename
        self._history_logger = HistoryLogger(self._interface)
        self._conversation_id = conversation_id
        self._bot_computing_answer = False

    async def index(self):
        return render_template("index.html", conversation_id=self._conversation_id)

    async def handle_input(self, textarea_index):
        textarea_index = int(textarea_index)
        query = request.form["query"]
        self._interface.input_queue.append(query)
        self._bot_computing_answer = True
        return get_html_from_dialogue_item(
            "bot: Typing...",
            textarea_index + 1,
            self._conversation_id,
            bot_is_computing_answer=True,
        )

    async def get_conversation_item(self, item_index):
        item_index = int(item_index)
        dialogue_items = self._interface.get_utterances_list_with_timestamp()
        if len(dialogue_items) <= item_index + 1:
            if self._bot_computing_answer:
                bot_text = "bot: Typing..."

            else:
                bot_text = "bot:"

            return get_html_from_dialogue_item(
                bot_text, item_index, self._conversation_id, bot_is_computing_answer=True
            )

        self._bot_computing_answer = False
        return get_html_from_dialogue_item(
            dialogue_items[item_index + 1][1],
            item_index,
            self._conversation_id,
            bot_is_computing_answer=False,
            reload_messages=True,
        )

    async def reset_conversation(self):
        self._interface.reset_history()
        self._bot_computing_answer = False
        await self._interface.output("Hello. How may I help you?")
        conversation = await self._get_conversation(append_empty_textarea=True)
        return conversation

    async def reload_rules(self):
        async with asyncio.Lock():
            self._knowledge.reload_rules(self._rules_filename)
            await self._knowledge.reinitialize_all_retrievers()
            print("Rules reloaded")

        return ""

    async def load_messages(self):
        conversation = await self._get_conversation(append_empty_textarea=True)
        return conversation

    async def handle_output(self):
        if not self._interface.output_queue:
            return jsonify({"text": "", "silent": False})

        output = self._interface.output_queue.pop(0)
        return jsonify(output)

    async def thumbs_up(self):
        self._history_logger.write("thumbs_up")
        return jsonify("")

    async def thumbs_down(self):
        self._history_logger.write("thumbs_down")
        return jsonify("")

    async def run(self):
        print(f"New web server instance {self._conversation_id} running!")
        return

    async def _get_conversation(self, append_empty_textarea=False):
        dialogue_items = self._interface.get_utterances_list_with_timestamp()
        dialogue = []
        for index, item in enumerate(dialogue_items):
            dialogue.append(
                (
                    item[0],
                    get_html_from_dialogue_item(
                        item[1],
                        index,
                        self._conversation_id,
                        bot_is_computing_answer=False,
                    ),
                )
            )
        if append_empty_textarea:
            dialogue.append(
                (
                    time.time(),
                    get_html_from_dialogue_item(
                        "user:",
                        index,
                        self._conversation_id,
                        bot_is_computing_answer=False,
                        autofocus=True,
                    ),
                )
            )
            if self._bot_computing_answer:
                bot_text = "bot: Typing..."

            else:
                bot_text = "bot:"

            dialogue.append(
                (
                    time.time(),
                    get_html_from_dialogue_item(
                        bot_text,
                        index + 1,
                        self._conversation_id,
                        bot_is_computing_answer=True,
                    ),
                )
            )

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
        conversation = (
            "<div id='dialogue' class='dialogue overflow-y-scroll rounded-lg'>"
        )
        conversation += "".join(dialogue_items)
        conversation += "</div>"
        conversation += "<div id='logs' class='logs shadow-lg overflow-y-scroll rounded-lg' style='flex-direction: column-reverse;'>"
        conversation += "".join(choices_and_facts)
        conversation += "</div>"
        return conversation
