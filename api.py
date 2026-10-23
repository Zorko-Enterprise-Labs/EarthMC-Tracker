import io
import os
import re
import threading
import requests
import map.api_interface as map_interface
from flask import Flask, request, send_file, render_template, send_from_directory
import sql
import players.api_interface as api_interface
import apikeys
import errors

app = Flask("API", template_folder="templates")
sql.initdb()

@app.route("/tiles/<path:filename>")
def serve_static_tiles(filename):
    return send_from_directory("tiles", filename)

@app.route("/status")
def download_status():
    # from map import server as map_server
    # return {"status": map_server.current_status}
    return {"status":True}

# Options
# Options
# Options

default_zoom_levels = [0,1,2,3,4,5]
default_time_radius = 3 # seconds

# Tiles are named like -12_7
tile_pattern = re.compile(r"-?\d+_-?\d+")

def getjson():
    # silent=True so a missing/wrong Content-Type gives our error instead of Flask's 415
    reqjson = request.get_json(silent=True)
    if not isinstance(reqjson, dict):
        return None
    return reqjson

def getidlist(reqjson, key : str):
    # Returns a list of ints, or None if the key isn't a list of ints
    ids = reqjson.get(key)
    if not isinstance(ids, list) or not all(isinstance(id, int) and not isinstance(id, bool) for id in ids):
        return None
    return ids

# Players API
# Players API
# Players API

@app.route("/players/takesnapshot", methods=['POST'])
def addsnapshot():
    reqjson = getjson()
    if not reqjson:
        return errors.geterror(4)

    if not apikeys.checkcreateperms(reqjson.get('apikey')):
        return errors.geterror(1)

    action = reqjson.get('action')
    if action == "track":
        if not reqjson.get('uuid'):
            return errors.geterror(6)
        try:
            uuid = sql.normaliseuuid(reqjson['uuid'])
        except ValueError:
            return errors.geterror(7, "uuid")

        try:
            coords = api_interface.easyfindplayer(uuid, api_interface.getcoordslist())
        except requests.RequestException:
            return errors.geterror(10)

        snapshotid, timestamp = sql.addsnapshot(coords['uuid'], coords['name'], coords['isOnline'], coords['x'], coords['y'], coords['z'], coords['yaw'])

        response = {
            'response' : coords,
            'databaseid' : snapshotid,
            'timestamp' : timestamp
        }
        return response

    if action == "fullsnapshot":
        try:
            coords = api_interface.getallcoords(api_interface.getcoordslist(), api_interface.getonlineplayers())
        except requests.RequestException:
            return errors.geterror(10)

        snapshotids, timestamp = sql.addsnapshots(coords)

        response = []
        for coord, snapshotid in zip(coords, snapshotids):
            playerentry = {
                'response' : coord,
                'databaseid' : snapshotid,
                'timestamp' : timestamp
            }
            response.append(playerentry)
        return response

    return errors.geterror(2)



@app.route("/players/deletesnapshot", methods=['POST'])
def deletesnapshot():
    reqjson = getjson()
    if not reqjson:
        return errors.geterror(4)

    if not apikeys.checkdeleteperms(reqjson.get('apikey')):
        return errors.geterror(1)

    if 'snapshotids' not in reqjson:
        return errors.geterror(6)

    todelete = getidlist(reqjson, 'snapshotids')
    if todelete is None:
        return errors.geterror(7, "snapshotids")

    if not todelete:
        return errors.geterror(5)

    # Nothing is deleted if any of the ids don't exist
    if not sql.deletesnapshots(todelete):
        return errors.geterror(3)

    response = {
        'deleted' : 'true'
    }
    return response



def formatgetresponse(snapshot):
    response = {
            'id' : snapshot['ID'],
            'isOnline' : bool(snapshot['playeronline']),
            'username' : snapshot['username'],
            'uuid' : snapshot['uuid'],
            'x' : snapshot['x'],
            'y' : snapshot['y'],
            'z' : snapshot['z'],
            'yaw' : snapshot['yaw'],
            'timestamp' : snapshot['Timestamp']
        }
    return response

@app.route("/players/getsnapshots", methods=['POST'])
def getsnapshot():
    reqjson = getjson()
    if not reqjson:
        return errors.geterror(4)

    if not apikeys.checkreadperms(reqjson.get('apikey')):
        return errors.geterror(1)

    if reqjson.get('id') is not None:
        try:
            snapshot = sql.getsnapshotfromid(int(reqjson['id']))
        except (TypeError, ValueError):
            return errors.geterror(7, "id")
        if not snapshot:
            return errors.geterror(3)
        return [formatgetresponse(snapshot)]

    uuid = None
    if reqjson.get('uuid'):
        try:
            uuid = sql.normaliseuuid(reqjson['uuid'])
        except ValueError:
            return errors.geterror(7, "uuid")

    # Optional: only snapshots within timeradius seconds of timestamp (unix seconds)
    timestamp = None
    timeradius = 0
    if reqjson.get('timestamp') is not None:
        try:
            timestamp = int(reqjson['timestamp'])
            timeradius = int(reqjson.get('timeradius', default_time_radius))
        except (TypeError, ValueError):
            return errors.geterror(7, "timestamp or timeradius")

    # REMEMBER TO ADD COORDINATE RADIUS THING

    snapshots = sql.getsnapshots(uuid, timestamp, timeradius)
    return [formatgetresponse(snapshot) for snapshot in snapshots]

# Map API
# Map API
# Map API

def onfinish(mapsnapshot : int):
    sql.setmapsnapshotfinished(mapsnapshot, True)

def formatgetsnapshotsresponse(snapshot):
    return {
        "id" : snapshot['ID'],
        "folderpath" : snapshot['folderpath'],
        "completed" : bool(snapshot['completed']),
        # maptiles/ isn't in git, so a snapshot made on another computer has no tiles here
        "available" : os.path.isdir(os.path.join(map_interface.defaultfolder, snapshot['folderpath'])),
        "timestamp" : snapshot['Timestamp']
    }

@app.route("/map/createsnapshot", methods=['POST'])
def createmapsnapshot():
    reqjson = getjson()
    if not reqjson:
        return errors.geterror(4)

    if not apikeys.checkcreateperms(reqjson.get('apikey')):
        return errors.geterror(1)

    zoomlevels = default_zoom_levels
    if reqjson.get('zoomlevels'):
        zoomlevels = getidlist(reqjson, 'zoomlevels')
        if zoomlevels is None:
            return errors.geterror(7, "zoomlevels")

    name = map_interface.getsuggestedtilespath()
    snapshotid = sql.addmapsnapshot(name, False)

    thread = threading.Thread(target=map_interface.downloadsnapshotbackground, args=(name,snapshotid,onfinish), kwargs={'zoomlevels': zoomlevels, 'verboselogging': False})
    thread.start()

    snapshot = sql.getmapsnapshotfromid(snapshotid)

    return {
        "snapshotid" : snapshotid,
        "snapshotpath" : name,
        "isfinished" : bool(snapshot['completed']),
        "timestamp" : snapshot['Timestamp']
    }

@app.route("/map/gettiles", methods=['POST', 'GET'])
def gettiles():
    if request.method == 'GET':
        reqdata = request.args
        if not reqdata:
            return errors.geterror(9)
        missingerror = 8
    else:
        reqdata = getjson()
        if not reqdata:
            return errors.geterror(4)
        missingerror = 6

    if not apikeys.checkreadperms(reqdata.get('apikey')):
        return errors.geterror(1)

    if reqdata.get('snapshotid') is None or reqdata.get('zoomlevel') is None or not reqdata.get('tile'):
        return errors.geterror(missingerror)

    try:
        inputtedid = int(reqdata.get('snapshotid'))
        inputtedzoomlevel = int(reqdata.get('zoomlevel'))
    except (TypeError, ValueError):
        return errors.geterror(7)

    inputtedtile = str(reqdata.get('tile'))
    if not tile_pattern.fullmatch(inputtedtile):
        return errors.geterror(7, "tile")

    mapsnapshot = sql.getmapsnapshotfromid(inputtedid)
    if not mapsnapshot:
        return errors.geterror(3)

    snapshot = map_interface.getsnapshot(mapsnapshot['folderpath'])
    if snapshot is None:
        return errors.geterror(3)

    zoomlevel = snapshot.getzoomlevel(inputtedzoomlevel)
    if zoomlevel is None:
        return errors.geterror(11)

    tilebinary = zoomlevel.getfile(f"{inputtedtile}.png")
    if tilebinary is None:
        return errors.geterror(11)

    return send_file(io.BytesIO(tilebinary), mimetype='image/png')

@app.route("/map/getsnapshots", methods=['POST'])
def getmapnapshots():
    reqjson = getjson()
    if not reqjson:
        return errors.geterror(4)

    if not apikeys.checkreadperms(reqjson.get('apikey')):
        return errors.geterror(1)

    if reqjson.get('id') is not None:
        try:
            snapshot = sql.getmapsnapshotfromid(int(reqjson['id']))
        except (TypeError, ValueError):
            return errors.geterror(7, "id")
        if not snapshot:
            return errors.geterror(3)
        return [formatgetsnapshotsresponse(snapshot)]

    return [formatgetsnapshotsresponse(snapshot) for snapshot in sql.getallmapsnapshots()]

@app.route("/map/deletesnapshots", methods=['POST'])
def deletemapsnapshot():
    reqjson = getjson()
    if not reqjson:
        return errors.geterror(4)

    if not apikeys.checkdeleteperms(reqjson.get('apikey')):
        return errors.geterror(1)

    if 'snapshotids' not in reqjson:
        return errors.geterror(6)

    todelete = getidlist(reqjson, 'snapshotids')
    if todelete is None:
        return errors.geterror(7, "snapshotids")

    if not todelete:
        return errors.geterror(5)

    # Nothing is deleted if any of the ids don't exist
    if not sql.deletemapsnapshots(todelete):
        return errors.geterror(3)

    response = {
        'deleted' : 'true'
    }
    return response


@app.route("/players/liveplayers", methods=["GET"])
def liveplayers():
    # Public route for the map to fetch live players seamlessly
    try:
        players = api_interface.getcachedcoordslist()
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Error fetching players: {e}")
        return errors.geterror(10)

    response = []
    for player in players:
        # The web map only shows the overworld
        if player.get('world', 'minecraft_overworld') != 'minecraft_overworld':
            continue
        response.append(api_interface.convertcoord(player, True))
    return response

@app.route("/players/search", methods=["GET"])
def search_player():
    username = request.args.get('username')
    if not username:
        return {"error": "No username provided"}, 400

    # Convert username to UUID in the backend as requested
    try:
        mojang_uuid = api_interface.getuuid(username)
    except requests.RequestException:
        return {"error": "Failed to look up username"}, 502
    if not mojang_uuid:
        return {"error": "Minecraft username not found"}, 404

    # Search for this UUID in the live EarthMC players
    try:
        player = api_interface.findplayer(mojang_uuid, api_interface.getcachedcoordslist())
    except requests.RequestException:
        return {"error": "Failed to fetch live coordinates"}, 502
    if player:
        return player
    return {"error": f"Player '{username}' is not currently online on the EarthMC map."}, 404

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    print("Running as main")
    app.run(host="127.0.0.1", port=5000)
