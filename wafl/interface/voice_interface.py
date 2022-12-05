import os
import random

from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.base_interface import BaseInterface
from wafl.interface.utils import get_most_common_words, not_good_enough
from wafl.listener.whisper_listener import WhisperListener
from wafl.speaker.fairseq_speaker import FairSeqSpeaker
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
        self._deny_sound_filename = self.__get_deny_sound_from_config(config)

        self.listener_model_name = config.get_value("listener_model")
        self._speaker = FairSeqSpeaker()
        self._listener = WhisperListener(self.listener_model_name)
        self._listener.set_timeout(config.get_value("listener_silence_timeout"))
        self._listener.set_volume_threshold(
            config.get_value("listener_volume_threshold")
        )
        self._listener.set_hotword_threshold(config.get_value("listener_hotword_logp"))
        self._bot_has_spoken = False
        self._check_understanding = True
        self._utterances = []

    def add_hotwords_from_knowledge(
        self, knowledge: "Knowledge", max_num_words: int = 100, count_threshold: int = 5
    ):
        hotwords = get_most_common_words(
            knowledge.get_facts_and_rule_as_text(),
            max_num_words=max_num_words,
            count_threshold=count_threshold,
        )
        hotwords = [word.lower() for word in hotwords]
        self._listener.add_hotwords(hotwords)

    def add_hotwords(self, hotwords):
        self._listener.add_hotwords(hotwords)

    def output(self, text: str):
        self._listener.activate()
        text = from_bot_to_user(text)
        self._utterances.append(f"bot: {text}")
        print(COLOR_START + "bot> " + text + COLOR_END)
        self._speaker.speak(text)
        self.bot_has_spoken(True)

    def input(self) -> str:
        text = ""
        while not text:
            text = self._listener.input()
            hotword = self._listener.get_hotword_if_present()
            if hotword:
                text = f"[{hotword}] {text}"

        while self._check_understanding and not_good_enough(text):
            print(COLOR_START + "user> " + text + COLOR_END)
            self.output(random.choice(["Sorry?", "Can you repeat?"]))
            text = self._listener.input()

        text = text.lower().capitalize()
        print(COLOR_START + "user> " + text + COLOR_END)
        utterance = from_user_to_bot(text)
        self._utterances.append(f"user: {utterance}")
        return utterance

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken

    def check_understanding(self, do_the_check=None):
        if do_the_check == None:
            return self._check_understanding

        if do_the_check and not self._check_understanding:
            self._sound_speaker.speak(self._activation_sound_filename)

        if not do_the_check and self._check_understanding:
            self._sound_speaker.speak(self._deactivation_sound_filename)

        self._check_understanding = do_the_check

    def play_deny_sound(self):
        self._sound_speaker.speak(self._deny_sound_filename)

    def get_utterances_list(self):
        return self._utterances

    def __get_activation_sound_from_config(self, config):
        if config.get_value("waking_up_sound"):
            return os.path.join(_path, "../sounds/activation.wav")

        return None

    def __get_deactivation_sound_from_config(self, config):
        if config.get_value("deactivate_sound"):
            return os.path.join(_path, "../sounds/deactivation.wav")

        return None

    def __get_deny_sound_from_config(self, config):
        if config.get_value("deny_sound"):
            return os.path.join(_path, "../sounds/deny.wav")

        return None
