class SwitchHandler:

    def __init__(self, controller):
      self.controller = controller

    def button_down(self, timestamp=None):
      pass

    def button_up(self, timestamp=None):
      self.controller.toggle()
