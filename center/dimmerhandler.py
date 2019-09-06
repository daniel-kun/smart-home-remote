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
        later = (when - datetime.utcnow()).total_seconds()
        return loop.call_later(later, callback, *args)

    def cancel(self, future):
        return future.cancel()

class DimmerHandler:

    DIM_UP = 1
    DIM_DOWN = 0

    def __init__(self, controller, scheduler):
        self.controller = controller
        self.scheduler = scheduler
        self.lastButtonDown = None
        self.startDimScheduledCall = None
        self.cancelDimScheduledCall = None
        self.nextDimDirection = self.DIM_UP

    def _startDim(self, direction, timestamp):
        self.controller.startDim(self.nextDimDirection)
        self.cancelDimScheduledCall = self.scheduler.call_at(timestamp + timedelta(seconds=10), self.controller.stopDim)
        if self.nextDimDirection == self.DIM_UP:
            self.nextDimDirection = self.DIM_DOWN
        else:
            self.nextDimDirection = self.DIM_UP

    def _stopDim(self):
        if self.cancelDimScheduledCall != None:
            self.scheduler.cancel(self.cancelDimScheduledCall)
        self.controller.stopDim()

    def button_down(self, timestamp=None):
        if timestamp == None:
            timestamp = datetime.utcnow()
        self.lastButtonDown = timestamp
        self.startDimScheduledCall = self.scheduler.call_at(timestamp + timedelta(milliseconds=600), self._startDim, self.nextDimDirection, timestamp)

    def button_up(self, timestamp=None):
        if timestamp == None:
            timestamp = datetime.utcnow()
        if (timestamp - self.lastButtonDown) <= timedelta(milliseconds=600):
            if self.startDimScheduledCall != None:
                self.scheduler.cancel(self.startDimScheduledCall)
            self.controller.toggle()
        else:
            self._stopDim()
