from datetime import datetime, timedelta
import asyncio

class AsyncIoScheduler:
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
        return loop.call_at(when, callback, *args)

    def cancel(self, loop, future):
        pass

class DimmerHandler:

    DIM_UP = 1
    DIM_DOWN = 0

    def __init__(self, controller, scheduler):
        self.controller = controller
        self.scheduler = scheduler
        self.lastButtonDown = None
        self.startDimScheduledCall = None
        self.nextDimDirection = self.DIM_UP

    def _startDim(self, direction):
        self.controller.startDim(self.nextDimDirection)
        if self.nextDimDirection == self.DIM_UP:
            self.nextDimDirection = self.DIM_DOWN
        else:
            self.nextDimDirection = self.DIM_UP

    def button_down(self, timestamp=datetime.now()):
        self.lastButtonDown = timestamp
        self.startDimScheduledCall = self.scheduler.call_at(timestamp + timedelta(milliseconds=600), self._startDim, self.nextDimDirection)

    def button_up(self, timestamp=datetime.now()):
        if (timestamp - self.lastButtonDown) <= timedelta(milliseconds=600):
            self.scheduler.cancel(self.startDimScheduledCall)
            self.controller.toggle()
        else:
            self.controller.stopDim()
