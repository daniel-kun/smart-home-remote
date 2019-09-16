class GiraDimmerController:
    def __init__(self, giraServie, dpDim, dpOnOff):
        self.giraService = giraServie
        self.dpDim = dpDim
        self.dpOnOff = dpOnOff

        self.giraService.load_cache(self.dpDim)
        self.giraService.load_cache(self.dpOnOff)

    def start_dim(self, direction):
        self.giraService.start_dim(self.dpDim, direction)

    def stop_dim(self):
        self.giraService.stop_dim(self.dpDim)

    def toggle(self):
        self.giraService.toggle(self.dpOnOff)
