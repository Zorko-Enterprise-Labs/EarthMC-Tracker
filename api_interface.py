import requests
import json

apikey = open('key.txt').read()
mojangusernameapi = 'https://api.mojang.com/users/profiles/minecraft/'
mojanguuidapi = 'https://api.mojang.com/user/profiles/'

apiurl = "https://api.earthmc.net/v4"
playerapiurl = f"{apiurl}/players/"
mapurl = "https://map.earthmc.net/tiles/players.json"

def getcoords():
    return json.loads(requests.get(mapurl).content)['players']

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

def checkonline(uuid : str):
    reqjson = '{"query": ["' + uuid + '"]}'

    response = json.loads(requests.post(playerapiurl, data=reqjson).content)
    
    if not response:
        return None
    
    status = response[0]['status']

    return status['isOnline']

def getuuid(username : str):
    url = mojangusernameapi + username
    response = json.loads(requests.get(url).content)

    if 'errorMessage' in str(response):
        return None
    if not response:
        return None

    return response['id']