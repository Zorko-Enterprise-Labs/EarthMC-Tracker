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
        return builderror("Request has no JSON content")
    return builderror("Unknown error")