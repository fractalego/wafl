import os
import random
import time

from wafl.events.utils import remove_text_between_brackets
from wafl.simple_text_processing.deixis import from_bot_to_user, from_user_to_bot
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
        super().__init__()
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

    def output(self, text: str, silent: bool = False):
        if silent:
            print(text)
            return

        if not text:
            return

        self._listener.activate()
        text = from_bot_to_user(text)
        self._utterances.append((time.time(), f"bot: {text}"))
        print(COLOR_START + "bot> " + text + COLOR_END)
        self._speaker.speak(text)
        self.bot_has_spoken(True)

    async def input(self) -> str:
        text = ""
        while not text:
            text = await self._listener.input()
            hotword = self._listener.get_hotword_if_present()
            if hotword:
                text = f"[{hotword}] {text}"

        while self._is_listening and not_good_enough(text):
            print(COLOR_START + "user> " + text + COLOR_END)
            self.output(random.choice(["Sorry?", "Can you repeat?"]))
            text = await self._listener.input()

        text = text.lower().capitalize()
        print(COLOR_START + "user> " + text + COLOR_END)
        utterance = remove_text_between_brackets(from_user_to_bot(text))
        if utterance.strip():
            self._utterances.append((time.time(), f"user: {text}"))

        return from_user_to_bot(text)

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken

    def activate(self):
        if not self._is_listening:
            self._sound_speaker.speak(self._activation_sound_filename)
            super().activate()

    def deactivate(self):
        if self._is_listening:
            self._sound_speaker.speak(self._deactivation_sound_filename)
            super().deactivate()

    def play_deny_sound(self):
        self._sound_speaker.speak(self._deny_sound_filename)

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
