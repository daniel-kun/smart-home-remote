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

    def start_dim(self, dpDim, direction):
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
        requests.put("https://{serverIp}/api/v1/values?token={token}".format(serverIp=self.serverIp, token=self.token), verify=False, data=values)
        print("GiraService.start_dim({})".format(direction))

    def stop_dim(self, dpDim):
        values = json.dumps({
            "values": [
                {
                    "uid": uid,
                    "value": "0"
                } for uid in dpDim
            ]
        })
        requests.put("https://{serverIp}/api/v1/values?token={token}".format(serverIp=self.serverIp, token=self.token), verify=False, data=values)
        print("GiraService.stop_dim()")

    def value(self, dpValue, value, offActionDPs):
        if (offActionDPs == None) or (not self.handle_off_action(offActionDPs)):
            values = json.dumps({
                "values": [
                    {
                        "uid": uid,
                        "value": value
                    } for uid in dpValue
                ]
            })
            requests.put("https://{serverIp}/api/v1/values?token={token}".format(serverIp=self.serverIp, token=self.token), verify=False, data=values)
            for uid in dpValue:
                self.valueCache[uid] = value
            print("GiraService.value({}, {}, {})".format(dpValue, value, offActionDPs))

    def switch(self, dpOnOff, onOrOff, offActionDPs):
        if (offActionDPs == None) or (not self.handle_off_action(offActionDPs)):
            value = 1 if onOrOff else 0
            values = json.dumps({
                "values": [
                    {
                        "uid": uid,
                        "value": value
                    } for uid in dpOnOff
                ]
            })
            requests.put("https://{serverIp}/api/v1/values?token={token}".format(serverIp=self.serverIp, token=self.token), verify=False, data=values)
            for uid in dpOnOff:
                self.valueCache[uid] = value
            print("GiraService.switch({})".format(onOrOff))

    def get_datapoint_value_sum(self, uids):
        if len(uids) == 0:
            return 0
        else:
            if uids[0] in self.valueCache:
                value = int(self.valueCache[uids[0]])
            else:
                value = 0 # Assume off if state is not known
            return value + self.get_datapoint_value_sum(uids[1:])

    def handle_off_action(self, offActionDPs):
        anyValueOn = self.get_datapoint_value_sum(offActionDPs) > 0
        if anyValueOn:
            # When any of the DPs are "on", switch them all off:
            print("GiraService: offAction executed, turning {} off".format(offActionDPs))
            self.switch(offActionDPs, False, None)
            return True
        else:
            # If they are all off, do nothing and signal the caller that no offAction
            # has been executed:
            return False

    def toggle(self, dpOnOff):
        currentState = self.get_datapoint_value_sum(dpOnOff)
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
        requests.put("https://{serverIp}/api/v1/values?token={token}".format(serverIp=self.serverIp, token=self.token), verify=False, data=values)
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

    def setup_web_app(self, app):
        app.add_routes([web.post('/value_changed', self.value_changed)])
        r = requests.post(
            "https://{serverIp}/api/v1/clients/{token}/callbacks".format(serverIp=self.serverIp, token=self.token),
            verify=False,
            data='{ "valueCallback": "https://maker-pi:8443/value_changed", "testCallbacks": false }',
            headers={"Content-Type": "application/json"})
        print(r)
