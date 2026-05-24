import json
from flask import Flask, url_for, request
import sql
import api_interface
import apikeys
import errors
from datetime import datetime, timedelta

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
        snapshotid = sql.getlatestsnapshot(uuid)[0]
        snapshot = sql.getsnapshotfromid(snapshotid)    
        
        response = {
            'response' : coords,
            'databaseid' : snapshotid,
            'timestamp' : snapshot[7]
        }
        return response

    if action == "fullsnapshot":
        coords = api_interface.getallcoords(api_interface.getcoordslist(), api_interface.getonlineplayers())
        response = []
        for coord in coords:
            uuid = coord['uuid']
            sql.addsnapshot(coord['uuid'], coord['isOnline'], coord['x'], coord['y'], coord['z'], coord['yaw'])
            snapshotid = sql.getlatestsnapshot(uuid)[0]
            snapshot = sql.getsnapshotfromid(snapshotid)

            playerentry = {
                'reponse' : coord,
                'databaseid' : snapshotid,
                'timestamp' : snapshot[7]
            }
            response.append(playerentry)
        return response

    return errors.geterror(0)



@app.route("/players/deletesnapshot", methods=['POST'])
def deletesnapshot():
    reqjson = request.json
    if not reqjson:
        return errors.geterror(4)
    
    if not apikeys.checkdeleteperms(reqjson['apikey']):
        return errors.geterror(1)

    todelete = reqjson['snapshotids']
    for id in todelete:
        if not id:
            return errors.geterror(3)
        # if not sql.getkey(id):
        #     return errors.geterror(3)
        sql.deletesnapshot(id)

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

def checktimestampradius(time1, time2, radius):
    if time1 > time2:
        if time1 - time2 <= radius:
            return True
        else:
            return False
    else:
        if time2 - time1 <= radius:
            return True
        else:
            return False 

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
        return [response]
    
    snapshots = sql.getallsnapshots()

    if reqjson.get('uuid'):
        snapshots = sql.getsnapshots(reqjson['uuid'])
    
    if reqjson.get('timestamp'):
        newsnapshots = []
        timestamp = reqjson['timestamp']
        
        if reqjson.get('timeradius'):
            timeradius = reqjson['timeradius']
        else:
            timeradius = 3
        
        for snapshot in snapshots:
            if checktimestampradius(timestamp, snapshot[7], timeradius):
                newsnapshots.append(snapshot)
        
        snapshots = newsnapshots

    # REMEMBER TO ADD COORDINATE RADIUS THING

    if snapshots == []:
        return []
    
    response = []
    for snapshot in snapshots:
        snapshotdata = sql.getsnapshotfromid(snapshot[0])
        response.append(formatgetresponse(snapshotdata, snapshotdata[1]))
    
    return response

app.run(debug=False)