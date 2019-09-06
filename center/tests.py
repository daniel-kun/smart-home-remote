import unittest
from unittest.mock import Mock
from datetime import datetime, timedelta
from dimmerhandler import DimmerHandler

class DimmerHandlerTests(unittest.TestCase):
    def test_short_press_should_toggle(self):
        """
        When receiving a button down followed by a button up signal
        in under 600 milliseconds, should send a toggle signal.
        """
        ctrl = Mock()
        sched = Mock()
        sut = DimmerHandler(ctrl, sched)
        timeButtonDown = datetime.now()
        sut.button_down(timestamp=timeButtonDown)
        sut.button_up(timestamp=timeButtonDown + timedelta(milliseconds=400))
        ctrl.toggle.assert_called_once()
        # sched.call_at.assert_called_once()
        # # Assert that a call has been scheduled in 600 ms. We assume that this call is the
        # # "begin dim" method.
        # self.assertEquals(sched.call_at.call_args[0][0], timeButtonDown + timedelta(milliseconds=600))
        # # Assert that the scheduled "begin dim" has been canceled:
        # sched.cancel.assert_called_once()

    def test_long_press_should_start_dim_and_stop_dim_and_not_toggle(self):
        """
        When receiving a button down followed by a button up signal
        in *more* than 600 milliseconds, should *not* send a toggle signal.
        """
        ctrl = Mock()
        sched = Mock()
        sut = DimmerHandler(ctrl, sched)
        timeButtonDown = datetime.now()
        sut.button_down(timestamp=timeButtonDown)
        sut.button_up(timestamp=timeButtonDown + timedelta(milliseconds=700))
        # Simulate the scheduled call:
        sched.call_at.call_args[0][1](sched.call_at.call_args[0][2])

        ctrl.toggle.assert_not_called()
        ctrl.startDim.assert_called_once()
        ctrl.stopDim.assert_called_once()

    def test_down_signal_without_up_signal_within_threshold_should_start_dim_up(self):
        """
        When receiving a button down *not* followed by a button up
        signal within the first 600 milliseconds, should start dimming
        up.
        """
        ctrl = Mock()
        sched = Mock()
        sut = DimmerHandler(ctrl, sched)
        timeButtonDown = datetime.now()

        sut.button_down(timestamp=timeButtonDown)
        # Simulate the scheduled call:
        sched.call_at.call_args[0][1](sched.call_at.call_args[0][2])

        ctrl.startDim.assert_called_once_with(DimmerHandler.DIM_UP)

    def test_down_signal_without_up_signal_within_threshold_should_dim_down_when_dimmed_up_before(self):
        """
        When receiving a button down *not* followed by a button up
        signal within the first 600 milliseconds, should start dimming
        down when previously has been dimmed up.
        """
        ctrl = Mock()
        sched = Mock()
        sut = DimmerHandler(ctrl, sched)
        timeButtonDown = datetime.now()
        sut.button_down(timestamp=timeButtonDown)
        # Simulate the scheduled call:
        sched.call_at.call_args[0][1](sched.call_at.call_args[0][2])
        sut.button_up(timestamp=timeButtonDown + timedelta(milliseconds=700))
        ctrl.reset_mock()
        sched.reset_mock()

        sut.button_down(timestamp=timeButtonDown + timedelta(seconds=4))
        # Simulate the scheduled call:
        sched.call_at.call_args[0][1](sched.call_at.call_args[0][2])

        print(ctrl.startDim.method_calls)
        ctrl.startDim.assert_called_once_with(DimmerHandler.DIM_DOWN)

    def test_up_signal_while_dimming_should_stop_dimming(self):
        """
        When currently dimming up or down, should stop dimming when
        button up signal has been received.
        """
        self.skipTest("To be implemented")

    def test_should_cancel_dimming_after_timeout(self):
        """
        When not receiving a button up signal within timeout when dimming,
        should cancel dimming to prevent endless dimming disturbing other
        attempts to control the light.
        """
        self.skipTest("To be implemented")

if __name__ == '__main__':
    unittest.main()
