class SceneHandler:

    def __init__(self, controller, sceneNumber):
        self.controller = controller
        self.sceneNumber = sceneNumber

    def button_down(self, timestamp=None):
        pass

    def button_up(self, timestamp=None):
        self.controller.value(self.sceneNumber)
