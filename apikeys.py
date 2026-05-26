import secrets
import sql

def gentoken():
    token = ""
    while True:
        token = secrets.token_urlsafe(16)
        if not sql.checkkeyexists(token):
            break
    return token

def addkey(createperms : bool, readperms : bool, deleteperms : bool):
    token = gentoken()
    sql.insertkey(token, createperms, readperms, deleteperms)
    return token

def getkey(key):
    keyid = sql.getkeyid(key)
    if not keyid:
        return False
    return sql.getkey(keyid[0][0])[0]

def checkcreateperms(apikey):
    key = getkey(apikey)
    if not key:
        return False
    if key[1]:
        return True
    else:
        return False
    
def checkreadperms(apikey):
    key = getkey(apikey)
    if not key:
        return False
    if key[2]:
        return True
    else:
        return False

def checkdeleteperms(apikey):
    key = getkey(apikey)
    if not key:
        return False
    if key[3]:
        return True
    else:
        return False