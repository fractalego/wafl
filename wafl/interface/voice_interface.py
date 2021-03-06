import os

from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.interface import BaseInterface
from wafl.interface.utils import get_most_common_words, not_good_enough
from wafl.listener.wav2vec2_listener import Wav2Vec2Listener
from wafl.speaker.festival_speaker import FestivalSpeaker
from wafl.speaker.soundfile_speaker import SoundFileSpeaker

_path = os.path.dirname(__file__)


COLOR_START = "\033[94m"
COLOR_END = "\033[0m"


class VoiceInterface(BaseInterface):
    def __init__(self, config):
        self._sound_speaker = SoundFileSpeaker()
        self._activation_sound_filename = self.__get_activation_sound_from_config(
            config
        )
        self._deactivation_sound_filename = self.__get_deactivation_sound_from_config(
            config
        )
        self.listener_model_name = config.get_value("listener_model")
        self._listener = Wav2Vec2Listener(self.listener_model_name)
        self._listener.set_timeout(0.6)
        self._listener.set_threshold(0.9)
        self._speaker = FestivalSpeaker()
        self._bot_has_spoken = False
        self._check_understanding = True

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

    def add_hotwords(self, hotwords):
        self._listener.add_hotwords(hotwords)

    def output(self, text: str):
        self._listener.activate()
        text = from_bot_to_user(text)
        print(COLOR_START + "bot> " + text + COLOR_END)
        self._speaker.speak(text)
        self.bot_has_spoken(True)

    def input(self) -> str:
        text = ""
        while not text:
            text = self._listener.input()

        while self._check_understanding and not_good_enough(text):
            print(COLOR_START + "user> " + text + COLOR_END)
            self.output("I did not quite understand that")
            text = self._listener.input()
        text = text.lower().capitalize()
        print(COLOR_START + "user> " + text + COLOR_END)
        return from_user_to_bot(text)

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken

    def check_understanding(self, do_the_check):
        if do_the_check and not self._check_understanding:
            self._sound_speaker.speak(self._activation_sound_filename)

        if not do_the_check and self._check_understanding:
            self._sound_speaker.speak(self._deactivation_sound_filename)

        self._check_understanding = do_the_check

    def __get_activation_sound_from_config(self, config):
        if config.get_value("waking_up_sound"):
            return os.path.join(_path, "../sounds/activation.wav")

        return None

    def __get_deactivation_sound_from_config(self, config):
        if config.get_value("deactivate_sound"):
            return os.path.join(_path, "../sounds/deactivation.wav")

        return None
