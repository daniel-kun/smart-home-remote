import json
from gira_service import GiraService
from gira_controller import GiraController
from dimmerhandler import DimmerHandler

def create_handler(conf, scheduler, services):
    if conf != None:
        if conf['type'] == 'Dimmer':
            dpDim1 = conf['functions'][0]['dataPoints']['Shift']
            dpOnOff1 = conf['functions'][0]['dataPoints']['OnOff']
            return DimmerHandler(GiraController(services['gira'], dpDim1, dpOnOff1), scheduler)
        else:
            return None
    else:
        return None

def create_config_from_json(j, scheduler, app):
    giraService = GiraService(j['server']['ip'], j['server']['access-token'])
    giraService.setupWebApp(app)
    services = {
        "gira": giraService
    }
    fullConfig = {int(key):create_handler(value, scheduler, services) for (key,value) in j['buttons'].items()}
    # Now remove items that have no handler:
    return {key:value for (key,value) in fullConfig.items() if value != None}

def load_config(file, scheduler, app):
    """
    Loads a config from a json file.
    
    Arguments:
    file: A path to a file that contains a valid json config (format to be documented)
    scheduler: An AsyncIO scheduler that can be used by the handlers
    app: An aiohttp Web App that is not yet started.
    """
    with open(file) as f:
        return create_config_from_json(json.load(f), scheduler, app)