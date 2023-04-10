import os
import time

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from wafl.interface.base_interface import BaseInterface
from wafl.interface.utils import not_good_enough

COLOR_START = "\033[94m"
COLOR_END = "\033[0m"
_path = os.path.dirname(__file__)
DEBUG = True
app = Flask(
    __name__,
    static_url_path="",
    static_folder=os.path.join(_path, "../frontend/"),
    template_folder=os.path.join(_path, "../frontend/"),
)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


class FlaskInterface(BaseInterface):
    def __init__(self):
        super().__init__()
        self._bot_has_spoken = False

    def output(self, text: str, silent: bool = False):
        if silent:
            print(text)
            return

        utterance = text
        print(COLOR_START + "bot> " + utterance + COLOR_END)
        self._utterances.append((time.time(), f"bot: {text}"))
        self.bot_has_spoken(True)

    async def input(self) -> str:
        text = input("user> ").strip()
        while not_good_enough(text):
            self.output("I did not quite understand that")
            text = input("user> ")

        self._utterances.append((time.time(), f"user: {text}"))
        return text

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken

    @app.route("/")
    def _return_index(self):
        return render_template("index.html")
