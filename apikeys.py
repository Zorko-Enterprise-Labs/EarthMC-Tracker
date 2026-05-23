import secrets
import sql

def gentoken():
    token = ""
    while True:
        token = secrets.token_urlsafe(16)
        if not sql.checkkeyexists(token):
            break
    return token

def addtoken(createperms : bool, readperms : bool):
    token = gentoken()
    sql.insertkey(token, createperms, readperms)
    return token

def checkcreateperms(key):
    keyid = sql.getkeyid(key)
    if not keyid:
        return False

    return sql.getkey(keyid[0][0])
    
def checkreadpems(key):
    keyid = sql.getkeyid(key)
    if not keyid:
        return False

    return sql.getkey(keyid[0][0])