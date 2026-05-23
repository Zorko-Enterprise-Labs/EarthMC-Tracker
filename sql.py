import sqlite3

filename = "snapshots.db"

con = sqlite3.connect(filename, check_same_thread=False)
cur = con.cursor()

def initdb():
    with open('schema.sql') as schema:
        with sqlite3.connect(filename) as conn:
            conn.cursor().executescript(schema.read())

def addsnapshot(uuid : str, x : int, y : int, z : int):
    cur.execute("""INSERT INTO snapshots (uuid, x, y, z) VALUES (?, ?, ?, ?) """,
        (uuid, x, y, z)    
    )
    
    con.commit()

def deletesnapshot(snapshotid : int):
    cur.execute("""DELETE FROM snapshots WHERE ID = ?""",
        (snapshotid,)
    )
    con.commit()

def getsnapshots(uuid : str):
    cur.execute("""SELECT ID FROM snapshots WHERE uuid = ? ORDER BY ID DESC""",
        (uuid,)
    )

    result = cur.fetchall()

    if result != [] and result != None:
        return result
    else:
        return None

def getlatestsnapshot(uuid : str):
    snapshots = getsnapshots(uuid)
    if not snapshots:
        return None
    return snapshots[0]

def getsnapshotfromid(snapshotid : int):
    cur.execute("""SELECT * FROM snapshots WHERE ID = ?""",
        (snapshotid,)
    )

    result = cur.fetchall()

    if result != [] and result != None:
        return result[0]
    else:
        return None

def insertkey(key : str, createperms : bool, readperms : bool):
    cur.execute("""INSERT INTO apikeys (createperms, readperms, apikey) VALUES (?,?,?)""",
        (createperms, readperms, key)
    )
    con.commit()

def removekey(id : int):
    cur.execute("""DELETE FROM apikeys WHERE ID = ?""",
        (id,)
    )
    con.commit()

def getkey(id : int):
    cur.execute("""SELECT * FROM apikeys WHERE ID = ?""",
        (id,)
    )

    return cur.fetchall()

def getkeyid(key : str):
    cur.execute("""SELECT ID FROM apikeys WHERE apikey = ? ORDER BY ID DESC""",
        (key,)
    )

    return cur.fetchall()