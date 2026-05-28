import json

def builderror(text, errorcode):
    errordict = {
        'error' : text,
        'errorcode' : errorcode
    }
    return json.dumps(errordict)

def geterror(error : int):
    if error == 1:
        return builderror("Insufficient permissions", 1)
    if error == 2:
        return builderror("Unknown action", 2)
    if error == 3:
        return builderror("Snapshot does not exist", 3)
    if error == 4:
        return builderror("Request has no JSON content", 4)
    if error == 5:
        return builderror("No snapshots were provided for deletion", 5)
    if error == 6:
        return builderror("JSON missing required keys", 6)
    if error == 7:
        return builderror("Key has incorrect type", 7)
    if error == 8:
        return builderror("Request args is missing a key", 8)
    if error == 9:
        return builderror("Request has no args", 9)
    if error == 10:
        return builderror("No such map snapshot exists", 10)
    return builderror("Unknown error", 0)