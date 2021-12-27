from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.interface import BaseInterface
from wafl.listener.wav2vec2_listener import Wav2Vec2Listener
from wafl.speaker.picotts_speaker import PiCoTTSSpeaker


class VoiceInterface(BaseInterface):
    def __init__(self):
        self._listener = Wav2Vec2Listener("facebook/wav2vec2-large-robust-ft-swbd-300h")
        self._listener.set_hotwords(
            [
                "COMPUTER",
                "JUBILEE",
                "LINE",
                "CAMDEN",
                "ADD",
                "REMOVE",
                "SHOPPING LIST",
                "APPLES",
            ]
        )
        self._listener.set_timeout(1.1)
        self._speaker = PiCoTTSSpeaker()

    def set_hot_words_from_text(self):
        pass

    def output(self, text: str):
        text = from_bot_to_user(text)
        print("bot>", text)
        self._speaker.speak(text)

    def input(self) -> str:
        text = self._listener.input()
        text = text.lower().capitalize()
        print("user>", text)
        return from_user_to_bot(text)
