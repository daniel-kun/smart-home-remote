class GiraSwitchController:
    def __init__(self, giraServie, dpOnOff):
        self.giraService = giraServie
        self.dpOnOff = dpOnOff
        self.giraService.load_cache(self.dpOnOff)

    def switch(self, onOrOff):
        self.giraService.switch(self.dpOnOff, onOrOff)

    def toggle(self):
        self.giraService.toggle(self.dpOnOff)
