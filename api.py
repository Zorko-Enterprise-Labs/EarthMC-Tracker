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
        return None
    
    if apikeys.checkcreateperms(reqjson['apikey']):
        action = reqjson['action']
        if action == "track":
            uuid = reqjson['uuid']

            coords = api_interface.easyfindplayer(uuid, api_interface.getcoordslist())
            
            print(coords)
            
            sql.addsnapshot(coords['uuid'], coords['isOnline'], coords['x'], coords['y'], coords['z'], coords['yaw'])
            snapshotid = sql.getlatestsnapshot(uuid)
            
            response = {
                'response' : coords,
                'databaseid' : snapshotid
            }
            return response

    return errors.geterror(1)

# @app.route("/players/deletesnapshot", methods=['POST'])
# def deletesnapshot():
#     reqjson = request.json
#     if not reqjson:
#         return None
    
#     # if apikeys.c
app.run(debug=False)