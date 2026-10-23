ERRORS = {
    0: ("Unknown error", 500),
    1: ("Insufficient permissions", 403),
    2: ("Unknown action", 400),
    3: ("Snapshot does not exist", 404),
    4: ("Request has no JSON content", 400),
    5: ("No snapshots were provided for deletion", 400),
    6: ("JSON missing required keys", 400),
    7: ("Key has incorrect type", 400),
    8: ("Request args is missing a key", 400),
    9: ("Request has no args", 400),
    10: ("EarthMC API is unavailable", 502),
    11: ("Tile does not exist", 404),
}

def builderror(text, errorcode, status):
    errordict = {
        'error' : text,
        'errorcode' : errorcode
    }
    return errordict, status

def geterror(error : int, detail : str = None):
    if error not in ERRORS:
        error = 0
    text, status = ERRORS[error]
    if detail:
        text = f"{text}: {detail}"
    return builderror(text, error, status)
