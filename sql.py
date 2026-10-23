import os
import json
import time
import sqlite3
import hashlib
import uuid as uuidlib
from contextlib import contextmanager

basedir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(basedir, "database.db")
schemafile = os.path.join(basedir, "schema.sql")

# Bump this and add a step to migrate() whenever schema.sql changes
SCHEMA_VERSION = 1

# Seconds to wait for another process/thread to finish writing (gunicorn runs several workers)
BUSY_TIMEOUT = 30

# Rows come back as sqlite3.Row, which works both as row[0] and row['ID']

@contextmanager
def connect():
    # One connection per call, so threads and workers never share a cursor
    conn = sqlite3.connect(filename, timeout=BUSY_TIMEOUT)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()

# Setup / migrations

def runscript(conn, script : str):
    # Like executescript(), but stays inside the current transaction
    statement = ""
    for line in script.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            conn.execute(statement)
            statement = ""

def tableexists(conn, table : str):
    return conn.execute("""SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?""",
        (table,)
    ).fetchone() is not None

def columns(conn, table : str):
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]

def initdb():
    # Every gunicorn worker calls this at startup, BEGIN IMMEDIATE makes them take turns
    conn = sqlite3.connect(filename, timeout=BUSY_TIMEOUT, isolation_level=None)
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            migrate(conn)
            conn.execute("COMMIT")
        except:
            conn.execute("ROLLBACK")
            raise

        # WAL lets reads and writes happen at the same time. It's saved in the file, so it only
        # has to succeed once, and switching doesn't wait for locks, so another worker may beat us to it
        if conn.execute("PRAGMA journal_mode").fetchone()[0] != "wal":
            try:
                conn.execute("PRAGMA journal_mode=WAL")
            except sqlite3.OperationalError:
                pass
    finally:
        conn.close()

def migrate(conn):
    version = conn.execute("PRAGMA user_version").fetchone()[0]

    with open(schemafile) as schema:
        schemasql = schema.read()

    if version < 1:
        # Pre-versioning database: rebuild every table from schema.sql, hashing api keys,
        # undashing uuids and turning old text timestamps into unix seconds on the way
        conn.create_function("normaliseuuid", 1, normaliseuuid)
        conn.create_function("hashkey", 1, lambda value: hashlib.sha256(value.encode()).hexdigest())

        transforms = {
            "Timestamp" : "CASE WHEN typeof(Timestamp) = 'text' THEN CAST(strftime('%s', Timestamp) AS INTEGER) ELSE Timestamp END",
            "uuid" : "normaliseuuid(uuid)",
            "playeronline" : "COALESCE(playeronline, 0)",
            "keyhash" : "hashkey(apikey)",
        }

        tables = ["mapsnapshots", "territorysnapshots", "snapshots", "trackedplayers", "apikeys"]
        oldtables = [table for table in tables if tableexists(conn, table)]
        for table in oldtables:
            conn.execute(f"ALTER TABLE {table} RENAME TO {table}_old")

        runscript(conn, schemasql)

        for table in oldtables:
            oldcolumns = columns(conn, f"{table}_old")
            newcolumns = [column for column in columns(conn, table)
                if column in oldcolumns or (column == "keyhash" and "apikey" in oldcolumns)]
            selects = [transforms.get(column, column) for column in newcolumns]
            conn.execute(f"""INSERT INTO {table} ({", ".join(newcolumns)}) SELECT {", ".join(selects)} FROM {table}_old""")
            conn.execute(f"DROP TABLE {table}_old")
    else:
        runscript(conn, schemasql)

    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

def normaliseuuid(value : str):
    # The map and Mojang use undashed uuids, the EarthMC API uses dashed ones. Store undashed.
    # Raises ValueError if it isn't a uuid.
    return uuidlib.UUID(str(value)).hex

# Shared helpers

def timeradius(timestamp : int, radius : int):
    return (timestamp - radius, timestamp + radius)

def deletemany(table : str, ids : list):
    # All or nothing: if any id doesn't exist, nothing is deleted
    ids = list(set(ids))
    placeholders = ", ".join("?" * len(ids))
    with connect() as conn:
        found = conn.execute(f"""SELECT COUNT(*) FROM {table} WHERE ID IN ({placeholders})""", ids).fetchone()[0]
        if found != len(ids):
            return False
        conn.execute(f"""DELETE FROM {table} WHERE ID IN ({placeholders})""", ids)
    return True

# Player snapshots

def addsnapshots(players : list, timestamp : int = None):
    # players are dicts with uuid, name, isOnline, x, y, z, yaw.
    # Everything goes in one transaction with one shared timestamp. Returns (ids, timestamp)
    if timestamp is None:
        timestamp = int(time.time())
    with connect() as conn:
        ids = []
        for player in players:
            cur = conn.execute("""INSERT INTO snapshots (uuid, username, playeronline, x, y, z, yaw, Timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (normaliseuuid(player['uuid']), player['name'], bool(player['isOnline']), player['x'], player['y'], player['z'], player['yaw'], timestamp)
            )
            ids.append(cur.lastrowid)
    return ids, timestamp

def addsnapshot(uuid : str, name : str, isOnline : bool, x : int, y : int, z : int, yaw : int):
    ids, timestamp = addsnapshots([{"uuid" : uuid, "name" : name, "isOnline" : isOnline, "x" : x, "y" : y, "z" : z, "yaw" : yaw}])
    return ids[0], timestamp

def deletesnapshot(snapshotid : int):
    return deletemany("snapshots", [snapshotid])

def deletesnapshots(snapshotids : list):
    return deletemany("snapshots", snapshotids)

def getsnapshots(uuid : str = None, timestamp : int = None, radius : int = 0):
    query = "SELECT * FROM snapshots WHERE 1 = 1"
    params = []
    if uuid:
        query += " AND uuid = ?"
        params.append(normaliseuuid(uuid))
    if timestamp is not None:
        query += " AND Timestamp BETWEEN ? AND ?"
        params.extend(timeradius(timestamp, radius))
    query += " ORDER BY ID DESC"

    with connect() as conn:
        return conn.execute(query, params).fetchall()

def getallsnapshots():
    return getsnapshots()

def getlatestsnapshot(uuid : str):
    with connect() as conn:
        return conn.execute("""SELECT * FROM snapshots WHERE uuid = ? ORDER BY ID DESC LIMIT 1""",
            (normaliseuuid(uuid),)
        ).fetchone()

def getsnapshotfromid(snapshotid : int):
    with connect() as conn:
        return conn.execute("""SELECT * FROM snapshots WHERE ID = ?""",
            (snapshotid,)
        ).fetchone()

def getsnapshotspath(uuid : str, start_ts : int = None, end_ts : int = None):
    # All snapshots of one player, oldest first, optionally within a time window
    query = "SELECT * FROM snapshots WHERE uuid = ?"
    params = [normaliseuuid(uuid)]
    if start_ts is not None:
        query += " AND Timestamp >= ?"
        params.append(start_ts)
    if end_ts is not None:
        query += " AND Timestamp <= ?"
        params.append(end_ts)
    query += " ORDER BY Timestamp ASC, ID ASC"

    with connect() as conn:
        return conn.execute(query, params).fetchall()

# Tracked players (the watchlist)

def addtrackedplayer(uuid : str, username : str):
    # Tracking an already tracked player keeps its original StartedAt
    with connect() as conn:
        conn.execute("""INSERT OR IGNORE INTO trackedplayers (uuid, username) VALUES (?, ?)""",
            (normaliseuuid(uuid), username)
        )

def removetrackedplayer(uuid : str):
    with connect() as conn:
        cur = conn.execute("""DELETE FROM trackedplayers WHERE uuid = ?""",
            (normaliseuuid(uuid),)
        )
        return cur.rowcount > 0

def getalltrackedplayers():
    with connect() as conn:
        return conn.execute("""SELECT * FROM trackedplayers ORDER BY StartedAt DESC""").fetchall()

def gettrackedplayerbyuuid(uuid : str):
    with connect() as conn:
        return conn.execute("""SELECT * FROM trackedplayers WHERE uuid = ?""",
            (normaliseuuid(uuid),)
        ).fetchone()

# Map snapshots

def addmapsnapshot(folderpath : str, completed : bool):
    with connect() as conn:
        cur = conn.execute("""INSERT INTO mapsnapshots (folderpath, completed) VALUES (?,?)""",
            (folderpath, completed)
        )
        return cur.lastrowid

def deletemapsnapshot(snapshotid : int):
    return deletemany("mapsnapshots", [snapshotid])

def deletemapsnapshots(snapshotids : list):
    return deletemany("mapsnapshots", snapshotids)

def getallmapsnapshots():
    with connect() as conn:
        return conn.execute("""SELECT * FROM mapsnapshots ORDER BY ID DESC""").fetchall()

def getmapsnapshottimeradius(timestamp : int, radius : int):
    with connect() as conn:
        return conn.execute("""SELECT * FROM mapsnapshots WHERE Timestamp BETWEEN ? AND ? ORDER BY ID DESC""",
            timeradius(timestamp, radius)
        ).fetchall()

def getmapsnapshotfromid(id : int):
    with connect() as conn:
        return conn.execute("""SELECT * FROM mapsnapshots WHERE ID = ?""",
            (id,)
        ).fetchone()

def getmapsnapshotbypath(path : str):
    with connect() as conn:
        return conn.execute("""SELECT * FROM mapsnapshots WHERE folderpath = ?""",
            (path,)
        ).fetchall()

def getmapsnapshotbytimestamp(timestamp : int):
    with connect() as conn:
        return conn.execute("""SELECT * FROM mapsnapshots WHERE Timestamp = ?""",
            (timestamp,)
        ).fetchall()

def getlatestmapsnapshot():
    with connect() as conn:
        return conn.execute("""SELECT * FROM mapsnapshots ORDER BY ID DESC LIMIT 1""").fetchone()

def setmapsnapshotfinished(snapshotid : int, isfinished : bool):
    with connect() as conn:
        conn.execute("""UPDATE mapsnapshots SET completed = ? WHERE ID = ?""",
            (isfinished, snapshotid)
        )

# Territory snapshots

def createterritorysnapshot(territoryname : str, polygons : list, nation : str, townboard : str, isCapital : bool, mapcolour : str):
    points = json.dumps(polygons)
    with connect() as conn:
        cur = conn.execute("""INSERT INTO territorysnapshots (points, townname, nation, townboard, iscapital, mapcolour) VALUES (?,?,?,?,?,?)""",
            (points, territoryname, nation, townboard, isCapital, mapcolour)
        )
        return cur.lastrowid

def getallterritorysnapshots():
    with connect() as conn:
        return conn.execute("""SELECT * FROM territorysnapshots ORDER BY ID DESC""").fetchall()

def deleteterritorysnapshot(id : int):
    return deletemany("territorysnapshots", [id])

def getterritorysnapshotbyid(id : int):
    with connect() as conn:
        return conn.execute("""SELECT * FROM territorysnapshots WHERE ID = ?""",
            (id,)
        ).fetchone()

def getterritorysnapshotbytimestamp(timestamp : int):
    with connect() as conn:
        return conn.execute("""SELECT * FROM territorysnapshots WHERE Timestamp = ?""",
            (timestamp,)
        ).fetchall()

def getterritorysnapshottimeradius(timestamp : int, radius : int):
    with connect() as conn:
        return conn.execute("""SELECT * FROM territorysnapshots WHERE Timestamp BETWEEN ? AND ? ORDER BY ID DESC""",
            timeradius(timestamp, radius)
        ).fetchall()

# API keys (only hashes are stored, see apikeys.py)

def insertkey(keyhash : str, createperms : bool, readperms : bool, deleteperms : bool):
    with connect() as conn:
        cur = conn.execute("""INSERT INTO apikeys (createperms, readperms, deleteperms, keyhash) VALUES (?,?,?,?)""",
            (createperms, readperms, deleteperms, keyhash)
        )
        return cur.lastrowid

def removekey(id : int):
    with connect() as conn:
        conn.execute("""DELETE FROM apikeys WHERE ID = ?""",
            (id,)
        )

def getkey(keyhash : str):
    with connect() as conn:
        return conn.execute("""SELECT * FROM apikeys WHERE keyhash = ?""",
            (keyhash,)
        ).fetchone()

def checkkeyexists(keyhash : str):
    return getkey(keyhash) is not None
