from datetime import datetime, timedelta

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

    def _start_dim(self, direction, timestamp):
        self.controller.start_dim(self.nextDimDirection)
        self.cancelDimScheduledCall = self.scheduler.call_at(timestamp + timedelta(seconds=10), self.controller.stop_dim)
        if self.nextDimDirection == self.DIM_UP:
            self.nextDimDirection = self.DIM_DOWN
        else:
            self.nextDimDirection = self.DIM_UP

    def _stop_dim(self):
        if self.cancelDimScheduledCall != None:
            self.scheduler.cancel(self.cancelDimScheduledCall)
        self.controller.stop_dim()

    def button_down(self, timestamp=None):
        if timestamp == None:
            timestamp = datetime.utcnow()
        self.lastButtonDown = timestamp
        self.startDimScheduledCall = self.scheduler.call_at(timestamp + timedelta(milliseconds=600), self._start_dim, self.nextDimDirection, timestamp)

    def button_up(self, timestamp=None):
        if timestamp == None:
            timestamp = datetime.utcnow()
        if (timestamp - self.lastButtonDown) <= timedelta(milliseconds=600):
            if self.startDimScheduledCall != None:
                self.scheduler.cancel(self.startDimScheduledCall)
            self.controller.toggle()
        else:
            self._stop_dim()
