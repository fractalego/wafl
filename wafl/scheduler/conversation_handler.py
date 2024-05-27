import asyncio
import random
import traceback

from wafl.exceptions import CloseConversation


class ConversationHandler:
    def __init__(
        self,
        interface,
        conversation,
        logger,
        activation_word="",
        max_misses=3,
        deactivate_on_closed_conversation=True,
    ):
        self._interface = interface
        self._conversation_events = conversation
        self._logger = logger
        self._activation_word = activation_word
        self._max_misses = max_misses
        self._deactivate_on_closed_conversation = deactivate_on_closed_conversation

    async def run(self):
        await self._say_initial_greetings()
        try:
            await self._main_loop()

        except (KeyboardInterrupt, EOFError):
            await self._interface.output("Good bye!")

    async def _say_initial_greetings(self):
        self._interface.activate()
        if self._activation_word:
            await self._interface.output(
                f"Please say '{self._activation_word}' to activate me"
            )
            self._interface.add_hotwords(self._activation_word)
            self._interface.deactivate()

    async def _main_loop(self):
        max_misses = self._max_misses
        num_misses = 0
        interactions = 0
        while True:
            await asyncio.sleep(0)
            if not self._interface.is_listening():
                interactions = 0
                num_misses = 0

            try:
                result = await self._conversation_events.process_next(
                    activation_word=self._activation_word
                )
                self._logger.write(
                    f"Conversation Result {result}", log_level=self._logger.level.INFO
                )
                interactions += 1
                if result:
                    self._interface.activate()

                if (
                    self._activation_word
                    and self._interface.bot_has_spoken()
                    and interactions == 1
                ):
                    self._interface.deactivate()
                    num_misses = 0

                if (
                    self._interface.is_listening()
                    and not result
                    and not self._interface.bot_has_spoken()
                ):
                    num_misses += 1
                    if max_misses > 0 and num_misses >= max_misses:
                        self._interface.deactivate()
                        self._interface.reset_history()

                    if interactions == 1:
                        await self._interface.output(
                            random.choice(["What can I do for you?"])
                        )

                    else:
                        await self._interface.output(
                            random.choice(["Sorry?", "Can you repeat?"])
                        )

                else:
                    num_misses = 0

            except CloseConversation:
                self._logger.write(
                    f"Closing the conversation", log_level=self._logger.level.INFO
                )
                if self._deactivate_on_closed_conversation:
                    self._interface.deactivate()

                else:
                    await self._interface.output("I am not sure what to reply.")

                continue

            except Exception as e:
                self._logger.write(
                    "Error in conversation loop", log_level=self._logger.level.ERROR
                )
                self._logger.write(str(e), log_level=self._logger.level.ERROR)
                print("Error in conversation loop. Closing the conversation.")
                await self._interface.output(
                    "Error in the conversation loop. Marking this conversation as a failure."
                )
                print(str(e))
                traceback.print_stack()
