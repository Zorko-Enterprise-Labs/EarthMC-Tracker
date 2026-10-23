import argparse
import hashlib
import secrets
import sql

def hashkey(apikey : str):
    return hashlib.sha256(apikey.encode()).hexdigest()

def gentoken():
    while True:
        token = secrets.token_urlsafe(16)
        if not sql.checkkeyexists(hashkey(token)):
            return token

def addkey(createperms : bool, readperms : bool, deleteperms : bool):
    token = gentoken()
    sql.insertkey(hashkey(token), createperms, readperms, deleteperms)
    return token

def getkey(apikey):
    if not isinstance(apikey, str) or not apikey:
        return None
    return sql.getkey(hashkey(apikey))

def checkcreateperms(apikey):
    key = getkey(apikey)
    return bool(key and key['createperms'])

def checkreadperms(apikey):
    key = getkey(apikey)
    return bool(key and key['readperms'])

def checkdeleteperms(apikey):
    key = getkey(apikey)
    return bool(key and key['deleteperms'])

if __name__ == "__main__":
    # python apikeys.py --create --read --delete
    parser = argparse.ArgumentParser(description="Create an API key. The key is only shown once, the database only keeps its hash.")
    parser.add_argument("--create", action="store_true", help="allow taking snapshots")
    parser.add_argument("--read", action="store_true", help="allow reading snapshots and tiles")
    parser.add_argument("--delete", action="store_true", help="allow deleting snapshots")
    args = parser.parse_args()

    sql.initdb()
    print(addkey(args.create, args.read, args.delete))
