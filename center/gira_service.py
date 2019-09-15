from aiohttp import web
import requests
import json

class GiraService:
    def __init__(self, serverIp, token):
        self.serverIp = serverIp
        self.token = token
        self.valueCache = dict()

    def load_cache(self, dpUid):
        for uid in dpUid:
            if not uid in self.valueCache:
                r = requests.get("https://{serverIp}/api/v1/values/{uid}?token={token}".format(serverIp=self.serverIp, uid=uid, token=self.token), verify=False)
                j = r.json()
                if 'values' in j:
                    for v in j['values']:
                        print("Cached value {} for {}".format(v['value'], v['uid']))
                        self.valueCache[v['uid']] = v['value']

    def startDim(self, dpDim, direction):
        if direction == 1:
            value = 100
        else:
            value = -100
        values = json.dumps({
            "values": [
                {
                    "uid": uid,
                    "value": value
                } for uid in dpDim
            ]
        })
        requests.put("https://{serverIp}/api/v1/values?token={token}".format(serverIp=self.serverIp, dpDim=dpDim, token=self.token), verify=False, data=values)
        print("GiraService.startDim({})".format(direction))

    def stopDim(self, dpDim):
        values = json.dumps({
            "values": [
                {
                    "uid": uid,
                    "value": "0"
                } for uid in dpDim
            ]
        })
        requests.put("https://{serverIp}/api/v1/values?token={token}".format(serverIp=self.serverIp, dpDim=dpDim, token=self.token), verify=False, data=values)
        print("GiraService.stopDim()")

    def switch(self, dpOnOff, onOrOff):
        value = 1 if onOrOff else 0
        values = json.dumps({
            "values": [
                {
                    "uid": uid,
                    "value": value
                } for uid in dpOnOff
            ]
        })
        requests.put("https://{serverIp}/api/v1/values?token={token}".format(serverIp=self.serverIp, dpOnOff=dpOnOff, token=self.token), verify=False, data=values)
        for uid in dpOnOff:
            self.valueCache[uid] = value
        print("GiraService.switch({})".format(onOrOff))

    def dpValuesSum(self, uids):
        if len(uids) == 0:
            return 0
        else:
            return int(self.valueCache[uids[0]]) + self.dpValuesSum(uids[1:])

    def toggle(self, dpOnOff):
        currentState = self.dpValuesSum(dpOnOff)
        if currentState > 0:
            value = 0 # If at least one light is on, turn all off
        else:
            value = 1 # If all are off, turn the lights on
        values = json.dumps({
            "values": [
                {
                    "uid": uid,
                    "value": value
                } for uid in dpOnOff
            ]
        })
        requests.put("https://{serverIp}/api/v1/values?token={token}".format(serverIp=self.serverIp, dpOnOff=dpOnOff, token=self.token), verify=False, data=values)
        for uid in dpOnOff:
            self.valueCache[uid] = value
        print("GiraService.toggle()")

    async def value_changed(self, request):
        payload = await request.json()
        print("Received value_changed: {}".format(json.dumps(payload)))
        if 'events' in payload:
            for e in payload['events']:
                if 'uid' in e and 'value' in e:
                    self.valueCache[e['uid']] = e['value']
        return web.Response(text="OK")

    def setupWebApp(self, app):
        app.add_routes([web.post('/value_changed', self.value_changed)])
        r = requests.post(
            "https://{serverIp}/api/v1/clients/{token}/callbacks".format(serverIp=self.serverIp, token=self.token),
            verify=False,
            data='{ "valueCallback": "https://maker-pi:8443/value_changed", "testCallbacks": false }',
            headers={"Content-Type": "application/json"})
        print(r)
