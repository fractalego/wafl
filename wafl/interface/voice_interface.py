from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.interface import BaseInterface
from wafl.interface.utils import get_most_common_words, not_good_enough
from wafl.listener.wav2vec2_listener import Wav2Vec2Listener
from wafl.speaker.festival_speaker import FestivalSpeaker


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
        self._speaker = FestivalSpeaker()

    def add_hotwords_from_knowledge(
        self, knowledge: "Knowledge", max_num_words: int = 100, count_threshold: int = 5
    ):
        hotwords = get_most_common_words(
            knowledge.get_facts_and_rule_as_text(),
            max_num_words=max_num_words,
            count_threshold=count_threshold,
        )
        hotwords = [word.upper() for word in hotwords]
        self._listener.add_hotwords(hotwords)

    def output(self, text: str):
        text = from_bot_to_user(text)
        print("bot>", text)
        self._speaker.speak(text)

    def input(self) -> str:
        text = ""
        while not_good_enough(text):
            if text:
                print("user>", text)
                self.output("I did not quite understand that")
            text = self._listener.input()
        text = text.lower().capitalize()
        print("user>", text)
        return from_user_to_bot(text)
