class GiraController:
    def __init__(self, giraServie, dpDim, dpOnOff):
        self.giraService = giraServie
        self.dpDim = dpDim
        self.dpOnOff = dpOnOff

        self.giraService.load_cache(self.dpDim)
        self.giraService.load_cache(self.dpOnOff)

    def startDim(self, direction):
        self.giraService.startDim(self.dpDim, direction)

    def stopDim(self):
        self.giraService.stopDim(self.dpDim)

    def toggle(self):
        self.giraService.toggle(self.dpOnOff)
