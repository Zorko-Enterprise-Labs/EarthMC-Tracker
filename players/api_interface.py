import time
import threading
import uuid as uuidlib
import requests
from sql import normaliseuuid

mojangusernameapi = 'https://api.mojang.com/users/profiles/minecraft/'

apiurl = "https://api.earthmc.net/v4"
mapurl = "https://map.earthmc.net/tiles/players.json"

# Seconds before giving up on EarthMC/Mojang, so a slow upstream can't hang a request forever
TIMEOUT = 10

# The web map polls every few seconds per open tab, so share one copy of players.json between them
CACHE_SECONDS = 2
coordscache = {"time" : 0, "players" : None}
coordscachelock = threading.Lock()

def getcoordslist():
    response = requests.get(mapurl, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()['players']

def getcachedcoordslist():
    with coordscachelock:
        if coordscache["players"] is None or time.time() - coordscache["time"] > CACHE_SECONDS:
            coordscache["players"] = getcoordslist()
            coordscache["time"] = time.time()
        return coordscache["players"]

def findplayer(uuid : str, coordslist):
    uuid = normaliseuuid(uuid)
    for coord in coordslist:
        if normaliseuuid(coord['uuid']) == uuid:
            return coord
    return None

def convertcoord(coord, isOnline : bool):
    return {
        "uuid": normaliseuuid(coord['uuid']),
        "name": coord['name'],
        "x": coord['x'],
        "y": coord['y'],
        "z": coord['z'],
        "yaw": coord['yaw'],
        "isOnline": isOnline
    }

def checkonline(uuid : str):
    # The EarthMC API only accepts dashed uuids and 404s on unknown players
    reqjson = {
        "query" : [str(uuidlib.UUID(uuid))]
    }
    response = requests.post(f"{apiurl}/players", json=reqjson, timeout=TIMEOUT)
    if response.status_code == 404:
        return False
    response.raise_for_status()
    players = response.json()
    if players:
        return bool(players[0]['status']['isOnline'])
    return False

def checkonlinemany(uuids : list):
    # One request for several players. Returns the set of (undashed) uuids that are online
    if not uuids:
        return set()
    reqjson = {
        "query" : [str(uuidlib.UUID(uuid)) for uuid in uuids]
    }
    response = requests.post(f"{apiurl}/players", json=reqjson, timeout=TIMEOUT)
    if response.status_code == 404:
        return set()
    response.raise_for_status()
    return {normaliseuuid(player['uuid']) for player in response.json() if player['status']['isOnline']}

def getprofile(username : str):
    # Returns (uuid, correctly capitalised name), or None if the username doesn't exist
    response = requests.get(mojangusernameapi + username, timeout=TIMEOUT)
    if response.status_code != 200:
        return None
    profile = response.json()
    return normaliseuuid(profile['id']), profile['name']

def getuuid(username : str):
    profile = getprofile(username)
    return profile[0] if profile else None

def getonlineplayers():
    response = requests.get(f"{apiurl}/online", timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()['players']

def getdummycoords(uuid, isOnline):
    return convertcoord({
            "uuid" : uuid,
            "name" : None,
            "x" : None,
            "y" : None,
            "z" : None,
            "yaw" : None
        },
            isOnline
        )

def easyfindplayer(uuid, coordslist):
    uuid = normaliseuuid(uuid)
    coords = findplayer(uuid, coordslist)
    isOnline = checkonline(uuid)

    if not coords:
        return getdummycoords(uuid, isOnline)

    return convertcoord(coords, isOnline)

def gettrackedcoords(uuids : list, coordslist):
    # Like easyfindplayer for a whole watchlist: anyone on the map is online,
    # everyone else is checked with a single EarthMC request
    coordsbyuuid = {normaliseuuid(coord['uuid']) : coord for coord in coordslist}
    uuids = [normaliseuuid(uuid) for uuid in uuids]
    online = checkonlinemany([uuid for uuid in uuids if uuid not in coordsbyuuid])

    result = []
    for uuid in uuids:
        if uuid in coordsbyuuid:
            result.append(convertcoord(coordsbyuuid[uuid], True))
        else:
            result.append(getdummycoords(uuid, uuid in online))
    return result

def getallcoords(coordslist, onlinelist):
    # Index the map once instead of searching it for every online player
    coordsbyuuid = {normaliseuuid(coord['uuid']) : coord for coord in coordslist}
    result = []
    for player in onlinelist:
        uuid = normaliseuuid(player['uuid'])
        coords = coordsbyuuid.get(uuid)

        if not coords:
            result.append(getdummycoords(uuid, True))
        else:
            result.append(convertcoord(coords, True))
    return result
