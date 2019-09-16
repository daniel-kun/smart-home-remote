class GiraValueController:
    def __init__(self, giraServie, dpValue, offActionDPs):
        self.giraService = giraServie
        self.dpValue = dpValue
        self.offActionDPs = offActionDPs
        self.giraService.load_cache(self.dpValue)
        if offActionDPs != None:
            for uid in offActionDPs:
                self.giraService.load_cache(uid)

    def value(self, value):
        self.giraService.value(self.dpValue, value, self.offActionDPs)
