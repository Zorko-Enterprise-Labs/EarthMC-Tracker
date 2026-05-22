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

def gettownfromid(townid : int):
    cur.execute("""SELECT * FROM towns WHERE id = ?""",
        (townid,)
    )

    result = cur.fetchall()

    if result != [] and result != None:
        return result[0]
    else:
        return None

def listtowns():
    cur.execute("""SELECT * FROM towns""")

    return cur.fetchall()

print(getsnapshots("tets"))