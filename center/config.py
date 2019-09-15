import json
from gira_service import GiraService
from gira_dimmer_controller import GiraDimmerController
from gira_switch_controller import GiraSwitchController
from dimmerhandler import DimmerHandler
from scene_handler import SceneHandler

def create_handler(conf, scheduler, services):
    if conf != None:
        if conf['type'] == 'Dimmer':
            dpDim = [fun['dataPoints']['Shift'] for fun in conf['functions']]
            dpOnOff = [fun['dataPoints']['OnOff'] for fun in conf['functions']]
            return DimmerHandler(GiraDimmerController(services['gira'], dpDim, dpOnOff), scheduler)
        elif conf['type'] == "Scene":
            dpScene = [fun['dataPoints']['Scene'] for fun in conf['functions']]
            return SceneHandler(GiraSwitchController(services['gira'], dpScene))
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