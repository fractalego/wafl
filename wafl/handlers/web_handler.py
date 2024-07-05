import asyncio
import os

from flask import render_template, request, jsonify

from wafl.config import Configuration
from wafl.connectors.clients.information_client import InformationClient
from wafl.interface.base_interface import BaseInterface
from wafl.logger.history_logger import HistoryLogger
from wafl.scheduler.messages_creator import MessagesCreator

_path = os.path.dirname(__file__)


class WebHandler:
    def __init__(
        self,
        interface: BaseInterface,
        config: Configuration,
        conversation_id: int,
        conversation_events: "ConversationEvents",
    ):
        self._interface = interface
        self._history_logger = HistoryLogger(self._interface)
        self._conversation_id = conversation_id
        self._conversation_events = conversation_events
        self._prior_dialogue_items = ""
        self._messages_creator = MessagesCreator(self._interface)
        self._information_client = InformationClient(config)

    async def index(self):
        return render_template("index.html", conversation_id=self._conversation_id)

    async def handle_input(self):
        query = request.form["query"]
        await self._interface.insert_input(query)
        return f"""
    <textarea id="query" type="text"
           class='shadow-lg w-full'
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
        await self._conversation_events.reload_knowledge()
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

    async def get_info(self):
        info = await self._information_client.get_information()
        is_clicked = request.form.get("clicked")
        is_clicked = "false" if is_clicked == "true" else "true"
        infobox = ""
        if is_clicked == "true":
            infobox = f"""
            <div class="bg-white shadow-lg rounded-lg p-4 absolute w-max left-20">
                <div style="color:black;font-size:12px;"><b>Model name:</b> {info['model_name']}</div>
                <div style="color:black;font-size:12px;"><b>Backend version:</b> {info['backend_version']}</div>
            </div>
            """
        return f"""
        <a title="Info"
           hx-post="/{self._conversation_id}/get_info"
           hx-vals='{{"clicked": "{is_clicked}"}}'
           hx-swap="outerHTML"
           class="flex items-center p-2 rounded-lg text-white hover:bg-gray-700 group">
           <svg fill="#FFFFFF" xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" class="w-6 h-6" viewBox="0 0 50 50">
           <path d="M 25 2 C 12.309295 2 2 12.309295 2 25 C 2 37.690705 12.309295 48 25 48 C 37.690705 48 48 37.690705 48 25 C 48 12.309295 37.690705 2 25 2 z M 25 4 C 36.609824 4 46 13.390176 46 25 C 46 36.609824 36.609824 46 25 46 C 13.390176 46 4 36.609824 4 25 C 4 13.390176 13.390176 4 25 4 z M 25 11 A 3 3 0 0 0 22 14 A 3 3 0 0 0 25 17 A 3 3 0 0 0 28 14 A 3 3 0 0 0 25 11 z M 21 21 L 21 23 L 22 23 L 23 23 L 23 36 L 22 36 L 21 36 L 21 38 L 22 38 L 23 38 L 27 38 L 28 38 L 29 38 L 29 36 L 28 36 L 27 36 L 27 21 L 26 21 L 22 21 L 21 21 z"></path>
           </svg>
            {infobox}
        </a>
        """

    async def run(self):
        print(f"New web server instance {self._conversation_id} running!")
        return
