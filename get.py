import requests
import json

url = "https://map.earthmc.net/tiles/players.json"

def getcoords():
    return json.loads(requests.get(url).content)['players']

def convertcoord(coords):
    return {
        "name": coord['name'],
        "uuid": coord['uuid'],
        "x": coord['x'],
        "y": coord['y'],
        "z": coord['z'],
        "yaw": coord['yaw']
    }

def findplayer(name, coordslist):
    for coord in coordslist:
        if coord['name'] == name:
            return coord
        
# def findplayerlist(name, coordslist):

# print(findplayer("cautionarytale08", getcoords()))
print(findplayer(input("username >"), getcoords()))