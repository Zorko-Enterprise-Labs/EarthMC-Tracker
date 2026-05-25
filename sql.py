import sqlite3

filename = "database.db"

con = sqlite3.connect(filename, check_same_thread=False)
cur = con.cursor()

with con:
    def initdb():
        with open('schema.sql') as schema:
            with sqlite3.connect(filename) as conn:
                conn.cursor().executescript(schema.read())

    def addsnapshot(uuid : str, isOnline : bool, x : int, y : int, z : int, yaw : int):
        cur.execute("""INSERT INTO snapshots (uuid, playeronline, x, y, z, yaw) VALUES (?, ?, ?, ?, ?, ?) """,
            (uuid, isOnline, x, y, z, yaw)    
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

    def getallsnapshots():
        cur.execute("""SELECT * FROM snapshots""")

        return cur.fetchall()



    def addmapsnapshot(folderpath : str, completed : bool):
        cur.execute("""INSERT INTO mapsnapshots (folderpath, completed) VALUES (?,?)""",
            (folderpath, completed)
        )
        con.commit()

    def deletemapsnapshot(snapshotid : int):
        cur.execute("""DELETE FROM mapsnapshots WHERE ID = ?""",
            (snapshotid,)
        )
        con.commit()

    def getallmapsnapshots():
        cur.execute("""SELECT * FROM mapsnapshots ORDER BY ID DESC""")
        return cur.fetchall()

    def getmapsnapshottimeradius(timestamp : int, timeradius : int):
        mapsnapshots = getallmapsnapshots()
        # if not cur.fetchall():
        #     return None
        # result = cur.fetchall()
        result = []
        for snapshot in mapsnapshots:
            snapshottimestamp = snapshot[3]
            difference = abs(timestamp - snapshottimestamp)
            if difference <= timeradius:
                result.append(snapshot)
        return result

    def getmapsnapshotbyid(id : int):
        cur.execute("""SELECT * FROM mapsnapshots WHERE ID = ?""",
            (id,)
        )
        return cur.fetchall()

    def getmapsnapshotbypath(path : str):
        cur.execute("""SELECT * FROM mapsnapshots WHERE folderpath = ?""",
            (path,)
        )
        return cur.fetchall()
    
    def getmapsnapshotbytimestamp(timestamp : int):
        cur.execute("""SELECT * FROM mapsnapshots WHERE Timestamp = ?""",
            (timestamp,)
        )
        return cur.fetchall()

    def getlatestmapsnapshot():
        snapshots = getallmapsnapshots()
        if not snapshots:
            return None
        return snapshots[0] 

    def setmapsnapshotfinished(snapshotid : int, isfinished : bool):
        cur.execute("""UPDATE mapsnapshots SET completed = ? WHERE ID = ?""",
            (isfinished, snapshotid)
        )
        con.commit()

    def insertkey(key : str, createperms : bool, readperms : bool, deleteperms : bool):
        cur.execute("""INSERT INTO apikeys (createperms, readperms, deleteperms, apikey) VALUES (?,?,?,?)""",
            (createperms, readperms, deleteperms, key)
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

    def checkkeyexists(apikey : str):
        if not getkeyid(apikey):
            return False
        return True 

    def getkeyid(key : str):
        cur.execute("""SELECT ID FROM apikeys WHERE apikey = ? ORDER BY ID DESC""",
            (key,)
        )

        return cur.fetchall()