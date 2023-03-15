import asyncio


class Scheduler:
    def __init__(self, loops_to_run_list):
        self._loops_to_run = [task.run() for task in loops_to_run_list]

    def run(self):
        asyncio.run(self._async_run())

    async def _async_run(self):
        await asyncio.gather(*self._loops_to_run, return_exceptions=True)
