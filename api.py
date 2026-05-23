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

# @app.route("/players/getsnapshot", methods=['POST'])
# def getsnapshot():
#     reqjson = request.json
#     if not reqjson:
#         return errors.geterror(4)
    
#     if not apikeys.checkreadperms(reqjson['apikey']):
#         return errors.geterror(1)
app.run(debug=False)