import secrets
import sql

def gentoken():
    return secrets.token_urlsafe(16)

def addtoken(createperms : bool, readperms : bool):
    token = gentoken()
    sql.insertkey(token, createperms, readperms)
    return token

def checkcreateperms(key):
    keyid = sql.getkeyid(key)
    return sql.getkey(keyid)

def checkreadpems(key):
    keyid = sql.getkeyid(key)
    return sql.getkey(keyid)