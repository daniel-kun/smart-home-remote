import requests
import os

serverIp    = os.getenv("SMARTHOMEREMOTE_SERVERIP")
dpDim       = os.getenv("SMARTHOMEREMOTE_DP_DIM")
dpOnOff     = os.getenv("SMARTHOMEREMOTE_DP_ONOFF")
token       = os.getenv("SMARTHOMEREMOTE_APITOKEN")

class GiraController:
    def startDim(self, direction):
        global dpDim, token
        if direction == 1:
            value = 100
        else:
            value = -100
        requests.put("https://{serverIp}/api/v1/values/{dpDim}?token={token}".format(serverIp=serverIp, dpDim=dpDim, token=token), verify=False, data='{{"value": {}}}'.format(value))
        print("GiraController.startDim({})".format(direction))

    def stopDim(self):
        global dpDim, token
        requests.put("https://{serverIp}/api/v1/values/{dpDim}?token={token}".format(serverIp=serverIp, dpDim=dpDim, token=token), verify=False, data='{"value": 0}')
        print("GiraController.stopDim()")

    def toggle(self):
        global dpOnOff, token
        r = requests.get("https://{serverIp}/api/v1/values/{dpOnOff}?token={token}".format(serverIp=serverIp, dpOnOff=dpOnOff, token=token), verify=False)
        result = r.json()
        value = 0
        if "values" in result:
            for v in result['values']:
                if "uid" in v and "value" in v:
                    if v['uid'] == "a00f":
                        value = int(v['value'])
        requests.put("https://{serverIp}/api/v1/values/{dpOnOff}?token={token}".format(serverIp=serverIp, dpOnOff=dpOnOff, token=token), verify=False, data='{{"value": {}}}'.format(1 - value))
        print("GiraController.toggle()")
