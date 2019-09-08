from aiohttp import web
import requests
import json

class GiraService:
    def __init__(self, serverIp, token):
        self.serverIp = serverIp
        self.token = token
        self.valueCache = dict()

    def load_cache(self, dpUid):
        if not dpUid in self.valueCache:
            r = requests.get("https://{serverIp}/api/v1/values/{dpUid}?token={token}".format(serverIp=self.serverIp, dpUid=dpUid, token=self.token), verify=False)
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
        requests.put("https://{serverIp}/api/v1/values/{dpDim}?token={token}".format(serverIp=self.serverIp, dpDim=dpDim, token=self.token), verify=False, data='{{"value": {}}}'.format(value))
        print("GiraController.startDim({})".format(direction))

    def stopDim(self, dpDim):
        requests.put("https://{serverIp}/api/v1/values/{dpDim}?token={token}".format(serverIp=self.serverIp, dpDim=dpDim, token=self.token), verify=False, data='{"value": 0}')
        print("GiraController.stopDim()")

    def toggle(self, dpOnOff):
        if dpOnOff in self.valueCache:
            value = 1 - int(self.valueCache[dpOnOff]) # Invert value
        else:
            value = 1 # Just turn on in case we don't know the value, yet
        requests.put("https://{serverIp}/api/v1/values/{dpOnOff}?token={token}".format(serverIp=self.serverIp, dpOnOff=dpOnOff, token=self.token), verify=False, data='{{"value": {}}}'.format(value))
        self.valueCache[dpOnOff] = str(value)
        print("GiraController.toggle()")

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
