import asyncio
import os

from flask import render_template, request, jsonify
from wafl.interface.queue_interface import QueueInterface
from wafl.logger.history_logger import HistoryLogger
from wafl.scheduler.web_interface_implementation import (
    get_html_from_dialogue_item,
)

_path = os.path.dirname(__file__)


class WebLoop:
    def __init__(
        self,
        interface: QueueInterface,
        conversation_id: int,
        conversation_events: "ConversationEvents",
    ):
        self._interface = interface
        self._history_logger = HistoryLogger(self._interface)
        self._conversation_id = conversation_id
        self._conversation_events = conversation_events
        self._prior_dialogue_items = ""

    async def index(self):
        return render_template("index.html", conversation_id=self._conversation_id)

    async def handle_input(self):
        query = request.form["query"]
        self._interface.input_queue.append(query)
        return f"""
    <textarea id="query" type="text"
           class='shadow-lg'
           placeholder="{query}"
           name="query"
           hx-post="/{self._conversation_id}/input"
           hx-swap="outerHTML"
           hx-target="#query"
           hx-trigger="keydown[!shiftKey&&keyCode==13]"
    ></textarea>
        """.strip()

    async def reset_conversation(self):
        self._interface.reset_history()
        self._interface.deactivate()
        self._interface.activate()
        self._conversation_events.reload_knowledge()
        self._conversation_events.reset_discourse_memory()
        await self._interface.output("Hello. How may I help you?")
        conversation = await self._get_conversation()
        return conversation

    async def reload_rules(self):
        async with asyncio.Lock():
            print("Not implemented yet")

        return ""

    async def check_for_new_messages(self):
        conversation = await self._get_conversation()
        if conversation != self._prior_dialogue_items:
            self._prior_dialogue_items = conversation
            return f"""
            <div id="load_conversation" 
               hx-post="/{self._conversation_id}/load_messages"
               hx-swap="innerHTML"
               hx-target="#messages"
               hx-trigger="load"
            ></div>"""

        else:
            self._prior_dialogue_items = conversation
            return "<div id='load_conversation'></div>"

    async def load_messages(self):
        conversation = await self._get_conversation()
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

    async def _get_conversation(self):
        dialogue_items = self._interface.get_utterances_list_with_timestamp()
        dialogue = []
        for index, item in enumerate(dialogue_items):
            dialogue.append(
                (
                    item[0],
                    get_html_from_dialogue_item(
                        item[1],
                    ),
                )
            )

        choices = self._interface.get_choices_and_timestamp()
        choices = [
            (
                item[0],
                "<div class='log-row'>" + item[1] + "</div>",
            )
            for item in choices
        ]
        facts = self._interface.get_facts_and_timestamp()
        facts = [
            (
                item[0],
                "<div class='log-row'>" + item[1] + "</div>",
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
        conversation += "<div id='logs' class='logs shadow-lg overflow-y-scroll rounded-lg width' style='flex-direction: column-reverse;'>"
        conversation += "".join(choices_and_facts)
        conversation += "</div>"
        return conversation
