import random

from wafl.exceptions import CloseConversation


class Scheduler:
    def __init__(self, interface, conversation, logger, activation_word=""):
        self._interface = interface
        self._conversation = conversation
        self._logger = logger
        self._activation_word = activation_word

    def run(self, max_misses=3):
        self._say_initial_greetings()
        try:
            self._main_loop(max_misses)

        except (KeyboardInterrupt, EOFError):
            self._conversation.output("Good bye!")

    def _say_initial_greetings(self):
        self._interface.activate()
        if self._activation_word:
            self._conversation.output(
                f"Please say '{self._activation_word}' to activate me"
            )
            self._interface.add_hotwords(self._activation_word)
            self._interface.deactivate()

    def _main_loop(self, max_misses):
        num_misses = 0
        interactions = 0
        while True:
            if not self._interface.is_listening():
                interactions = 0
                num_misses = 0

            try:
                result = self._conversation.input(activation_word=self._activation_word)
                self._logger.write(
                    f"Conversation Result {result}", log_level=self._logger.level.INFO
                )
                interactions += 1
                if result:
                    self._interface.activate()

                if self._interface.bot_has_spoken() and interactions == 1:
                    self._interface.deactivate()
                    num_misses = 0

                if (
                    self._interface.is_listening()
                    and not result
                    and not self._interface.bot_has_spoken()
                ):
                    num_misses += 1
                    if num_misses >= max_misses:
                        self._interface.deactivate()

                    if interactions <= 1:
                        self._interface.output(
                            random.choice(["What can I do for you?"])
                        )

                    else:
                        self._interface.output(
                            random.choice(["Sorry?", "Can you repeat?"])
                        )

                else:
                    num_misses = 0

            except CloseConversation:
                self._logger.write(
                    f"Closing the conversation", log_level=self._logger.level.INFO
                )
                self._interface.deactivate()
                continue
