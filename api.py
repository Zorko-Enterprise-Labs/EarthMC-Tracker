import json
from flask import Flask, url_for, request
import sql
import api_interface
import apikeys
import errors

app = Flask("API")

@app.route("/players/takesnapshot", methods=['POST'])
def addsnapshot():
    reqjson = request.json
    if not reqjson:
        return errors.geterror(4)
    
    if not apikeys.checkcreateperms(reqjson['apikey']):
        return errors.geterror(1)
    
    action = reqjson['action']
    if action == "track":
        uuid = reqjson['uuid']
        coords = api_interface.easyfindplayer(uuid, api_interface.getcoordslist())
            
        sql.addsnapshot(coords['uuid'], coords['isOnline'], coords['x'], coords['y'], coords['z'], coords['yaw'])
        snapshotid = sql.getlatestsnapshot(uuid)
            
        response = {
            'response' : coords,
            'databaseid' : snapshotid
        }
        return response

    return errors.geterror(0)

@app.route("/players/deletesnapshot", methods=['POST'])
def deletesnapshot():
    reqjson = request.json
    if not reqjson:
        return errors.geterror(4)
    
    if not apikeys.checkdeleteperms(reqjson['apikey']):
        return errors.geterror(1)

    todelete = int(reqjson['snapshotid'])

    if not sql.getkey(todelete):
        return errors.geterror(3)

    sql.deletesnapshot(todelete)

    response = {
        'deleted' : 'true'
    }
    return response

def formatgetresponse(snapshot, isOnline):
    response = {
            'id' : snapshot[0],
            'isOnline' : isOnline,
            'uuid' : snapshot[2],
            'x' : snapshot[3],
            'y' : snapshot[4],
            'z' : snapshot[5],
            'yaw' : snapshot[6],
            'timestamp' : snapshot[7]
        }
    return response

@app.route("/players/getsnapshots", methods=['POST'])
def getsnapshot():
    reqjson = request.json
    if not reqjson:
        return errors.geterror(4)

    if not apikeys.checkreadperms(reqjson['apikey']):
        return errors.geterror(1)

    if reqjson.get('id'):
        snapshot = sql.getsnapshotfromid(reqjson['id'])
        isOnlineRaw = snapshot[1]
        if isOnlineRaw:
            isOnline = True
        else:
            isOnline = False

        response = formatgetresponse(snapshot, isOnline)
        # return json.dumps(snapshot)
        return [response]
    return "hi"

app.run(debug=False)