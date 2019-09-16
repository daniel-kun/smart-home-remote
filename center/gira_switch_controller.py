class GiraSwitchController:
    def __init__(self, giraServie, dpOnOff, offActionDPs):
        self.giraService = giraServie
        self.dpOnOff = dpOnOff
        self.offActionDPs = offActionDPs
        self.giraService.load_cache(self.dpOnOff)
        if offActionDPs != None:
            for uid in offActionDPs:
                self.giraService.load_cache(uid)

    def switch(self, onOrOff):
        self.giraService.switch(self.dpOnOff, onOrOff, self.offActionDPs)

    def toggle(self):
        self.giraService.toggle(self.dpOnOff, self.offActionDPs)
