import os
import random
import re
import time

from wafl.events.utils import remove_text_between_brackets
from wafl.simple_text_processing.deixis import from_bot_to_user
from wafl.interface.base_interface import BaseInterface
from wafl.interface.utils import get_most_common_words, not_good_enough
from wafl.listener.whisper_listener import WhisperListener
from wafl.speaker.fairseq_speaker import FairSeqSpeaker
from wafl.speaker.soundfile_speaker import SoundFileSpeaker

_path = os.path.dirname(__file__)


COLOR_START = "\033[94m"
COLOR_END = "\033[0m"


class VoiceInterface(BaseInterface):
    def __init__(self, config, output_filter=None):
        super().__init__()
        self._sound_speaker = SoundFileSpeaker()
        self._activation_sound_filename = self.__get_activation_sound_from_config(
            config
        )
        self._deactivation_sound_filename = self.__get_deactivation_sound_from_config(
            config
        )
        self.listener_model_name = config.get_value("listener_model")["local_model"]
        self._speaker = FairSeqSpeaker(config)
        self._listener = WhisperListener(config)
        self._listener.set_timeout(
            config.get_value("listener_model")["listener_silence_timeout"]
        )
        self._listener.set_volume_threshold(
            config.get_value("listener_model")["listener_volume_threshold"]
        )
        self._listener.set_hotword_threshold(
            config.get_value("listener_model")["listener_hotword_logp"]
        )
        self._bot_has_spoken = False
        self._utterances = []
        self._output_filter = output_filter

    async def add_hotwords_from_knowledge(
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

    async def output(self, text: str, silent: bool = False):
        if silent:
            print(text)
            return

        if not text:
            return

        if self._output_filter:
            text = await self._output_filter.filter(
                self.get_utterances_list_with_timestamp(), text
            )

        self._listener.activate()
        text = from_bot_to_user(text)
        self._utterances.append((time.time(), f"bot: {text}"))
        print(COLOR_START + "bot> " + text + COLOR_END)
        await self._speaker.speak(text)
        self.bot_has_spoken(True)

    async def input(self) -> str:
        text = ""
        while not text:
            text = await self._listener.input()
            text = self.__remove_activation_word_and_normalize(text)
            hotword = await self._listener.get_hotword_if_present()
            if hotword:
                text = f"[{hotword}] {text}"

        while self._is_listening and not_good_enough(text):
            print(COLOR_START + "user> " + text + COLOR_END)
            await self.output(random.choice(["Sorry?", "Can you repeat?"]))
            text = await self._listener.input()

        text = text.lower().capitalize()
        print(COLOR_START + "user> " + text + COLOR_END)
        utterance = remove_text_between_brackets(text)
        if utterance.strip():
            self._utterances.append((time.time(), f"user: {text}"))

        return text

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

    def __get_activation_sound_from_config(self, config):
        if config.get_value("waking_up_sound"):
            return os.path.join(_path, "../sounds/activation.wav")

        return None

    def __get_deactivation_sound_from_config(self, config):
        if config.get_value("deactivate_sound"):
            return os.path.join(_path, "../sounds/deactivation.wav")

        return None

    def __remove_activation_word_and_normalize(self, text):
        activation_word = re.sub(r"\[(.*)\].*", r"\1", text)
        text = re.sub(
            f"^\[{activation_word}\] {activation_word} (.*)",
            r"\1",
            text,
            flags=re.IGNORECASE,
        )
        return text
