from aiohttp import web

class GiraService:
    def __init__(self, serverIp, token):
        self.serverIp = serverIp
        self.token = token

    async def valueChanged(self, request):
        payload = await request.json()
        if 'events' in payload:
            for e in payload['events']:
                if 'uid' in e and 'value' in e:
                    print("UID {} changed to value {}".format(e['uid'], e['value']))
        return web.Response(text="OK")

    def setupWebApp(self, app):
        app.add_routes([web.post('/value_changed', self.valueChanged)])
