import json

def builderror(text):
    errordict = {
        'error' : text
    }
    return json.dumps(errordict)

def geterror(error : int):
    if error == 1:
        return builderror("Insufficient permissions")
    if error == 2:
        return builderror("No such player is visible on the map")
    return builderror("Unknown error")