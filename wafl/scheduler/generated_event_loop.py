class GeneratedEventLoop:
    def __init__(self, interface, events, logger):
        self._interface = interface
        self._events = events
        self._logger = logger

    async def run(self):
        try:
            await self._events.process_next()

        except (KeyboardInterrupt, EOFError) as e:
            self._logger.write(
                f"The Generated event loop has ended due to exception {str(e)}"
            )
