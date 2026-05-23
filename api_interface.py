import uuid
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

def findplayer(uuid, coordslist):
    for coord in coordslist:
        if coord['uuid'] == uuid:
            return coord

def convertcoord(coord, isOnline : bool):
    return {
        "uuid": coord['uuid'],
        "x": coord['x'],
        "y": coord['y'],
        "z": coord['z'],
        "yaw": coord['yaw'],
        "isOnline": isOnline
    }

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

    return str(uuid.UUID(hex=response['id']))

def getallcoords():
    playerlist = getcoords()
    result = []
    for player in playerlist:
        result.append(convertcoord(player))
    return result

def getonlineplayers():
    url = f"{apiurl}/online"
    response = requests.get(url).content
    return json.loads(response)['players']

def checkonline(uuid : str):
    url = f"{apiurl}/players"
    reqjson = {
        "query" : [uuid]
    }
    response = json.loads(requests.post(url, json=reqjson).content)
    if response:
        return response[0]['status']['isOnline']
    else:
        return False

def easyfindplayer(uuid):
    req = getcoords()
    coords = findplayer(uuid, req)
    isOnline = checkonline(uuid)

    if not coords:
        return convertcoord({
            "uuid" : uuid,
            "x" : None,
            "y" : None,
            "z" : None,
            "yaw" : None
        },
            isOnline
        )

    return convertcoord(coords, isOnline)
print(easyfindplayer(getuuid("cautionarytale08")))