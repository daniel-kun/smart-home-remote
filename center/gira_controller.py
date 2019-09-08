import requests
import os

class GiraController:
    def __init__(self, giraServie, dpDim, dpOnOff):
        self.giraService = giraServie
        self.dpDim = dpDim
        self.dpOnOff = dpOnOff

    def startDim(self, direction):
        if direction == 1:
            value = 100
        else:
            value = -100
        requests.put("https://{serverIp}/api/v1/values/{dpDim}?token={token}".format(serverIp=self.giraService.serverIp, dpDim=self.dpDim, token=self.giraService.token), verify=False, data='{{"value": {}}}'.format(value))
        print("GiraController.startDim({})".format(direction))

    def stopDim(self):
        requests.put("https://{serverIp}/api/v1/values/{dpDim}?token={token}".format(serverIp=self.giraService.serverIp, dpDim=self.dpDim, token=self.giraService.token), verify=False, data='{"value": 0}')
        print("GiraController.stopDim()")

    def toggle(self):
        r = requests.get("https://{serverIp}/api/v1/values/{dpOnOff}?token={token}".format(serverIp=self.giraService.serverIp, dpOnOff=self.dpOnOff, token=self.giraService.token), verify=False)
        result = r.json()
        value = 0
        if "values" in result:
            for v in result['values']:
                if "uid" in v and "value" in v:
                    if v['uid'] == self.dpOnOff:
                        value = int(v['value'])
        requests.put("https://{serverIp}/api/v1/values/{dpOnOff}?token={token}".format(serverIp=self.giraService.serverIp, dpOnOff=self.dpOnOff, token=self.giraService.token), verify=False, data='{{"value": {}}}'.format(1 - value))
        print("GiraController.toggle()")
