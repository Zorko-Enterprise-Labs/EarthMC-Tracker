import requests
import json

url = "https://map.earthmc.net/tiles/players.json"

def getcoords():
    return json.loads(requests.get(url).content)['players']

def findplayer(name, coordslist):
    for coord in coordslist:
        if coord['name'] == name:
            return coord

def convertcoord(coord):
    return {
        "name": coord['name'],
        "uuid": coord['uuid'],
        "x": coord['x'],
        "y": coord['y'],
        "z": coord['z'],
        "yaw": coord['yaw']
    }

def easyfindplayer(username):
    req = getcoords()
    coords = findplayer(username, req)
    
    if not coords:
        return None

    return convertcoord(coords)