import asyncio
import os

from flask import render_template, request, jsonify
from wafl.interface.base_interface import BaseInterface
from wafl.logger.history_logger import HistoryLogger
from wafl.scheduler.messages_creator import MessagesCreator

_path = os.path.dirname(__file__)


class WebHandler:
    def __init__(
        self,
        interface: BaseInterface,
        conversation_id: int,
        conversation_events: "ConversationEvents",
    ):
        self._interface = interface
        self._history_logger = HistoryLogger(self._interface)
        self._conversation_id = conversation_id
        self._conversation_events = conversation_events
        self._prior_dialogue_items = ""
        self._messages_creator = MessagesCreator(self._interface)

    async def index(self):
        return render_template("index.html", conversation_id=self._conversation_id)

    async def handle_input(self):
        query = request.form["query"]
        await self._interface.insert_input(query)
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
        conversation = await self._messages_creator.get_messages_window()
        return conversation

    async def reload_rules(self):
        async with asyncio.Lock():
            print("Not implemented yet")

        return ""

    async def check_for_new_messages(self):
        conversation = await self._messages_creator.get_messages_window()
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
        conversation = await self._messages_creator.get_messages_window()
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

    async def toggle_logs(self):
        self._messages_creator.toggle_logs()
        return jsonify("")

    async def run(self):
        print(f"New web server instance {self._conversation_id} running!")
        return
