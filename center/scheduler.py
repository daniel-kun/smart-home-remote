from datetime import datetime
import asyncio

class Scheduler:
    def __init__(self, loop):
        self.loop = loop

    def call_at(self, when, callback, *args):
        """
        Schedules a `callback` to be run at time `when` with `args`.
        Uses asyncio.call_at().
        """
        if self.loop == None:
            loop = asyncio.get_running_loop()
        else:
            loop = self.loop
        later = (when - datetime.utcnow()).total_seconds()
        return loop.call_later(later, callback, *args)

    def cancel(self, future):
        return future.cancel()
