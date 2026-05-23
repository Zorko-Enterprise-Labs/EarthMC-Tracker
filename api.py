from flask import Flask, url_for, request
import sql
import api_interface
import apikeys
import errors

app = Flask("API")

@app.route("/players/takesnapshot", methods=['POST'])
def snapshot():
    reqjson = request.json
    if not reqjson:
        return None
    
    if apikeys.checkcreateperms(reqjson['apikey']):
        action = reqjson['action']
        if action == "track":
            uuid = reqjson['uuid']

            coords = api_interface.easyfindplayer(uuid)
            if coords == None:
                return errors.geterror(2)
            
            sql.addsnapshot(coords['uuid'], coords['isOnline'], coords['x'], coords['y'], coords['z'])
            snapshotid = sql.getlatestsnapshot(uuid)
            
            response = {
                'response' : coords,
                'databaseid' : snapshotid
            }
            return response

    return errors.geterror(1)

app.run(debug=False)