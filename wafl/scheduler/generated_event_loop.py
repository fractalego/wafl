class GeneratedEventLoop:
    def __init__(self, interface, events, logger):
        self._interface = interface
        self._events = events
        self._logger = logger

    async def run(self):
        try:
            await self._events.process_next()

        except (KeyboardInterrupt, EOFError):
            self._interface.output("Good bye!")
