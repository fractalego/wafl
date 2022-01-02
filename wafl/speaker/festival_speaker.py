import subprocess

from wafl.speaker.base_speaker import BaseSpeaker


class FestivalSpeaker(BaseSpeaker):
    def __init__(self, voice="british_english"):
        self._voice = voice

    def speak(self, text):
        proc = subprocess.Popen(
            "festival --tts --language british_english -",
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.communicate(bytes(text, "utf-8"))
