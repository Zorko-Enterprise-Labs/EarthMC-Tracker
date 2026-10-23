-- Safe to run on an existing database: nothing here drops or overwrites data.
-- Timestamps are unix seconds (UTC). UUIDs are stored undashed, lowercase (same as the map).
-- Don't put semicolons inside comments, sql.py splits this file on them.

CREATE TABLE IF NOT EXISTS mapsnapshots (
    ID INTEGER PRIMARY KEY,
    folderpath TEXT NOT NULL,
    completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)),
    Timestamp INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS mapsnapshots_timestamp ON mapsnapshots (Timestamp);

CREATE TABLE IF NOT EXISTS territorysnapshots (
    ID INTEGER PRIMARY KEY,
    points TEXT NOT NULL CHECK (json_valid(points)),   -- JSON array of [x, z] points
    townname TEXT NOT NULL,
    nation TEXT NOT NULL,
    townboard TEXT NOT NULL,
    iscapital BOOLEAN NOT NULL CHECK (iscapital IN (0, 1)),
    mapcolour TEXT NOT NULL,
    Timestamp INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS territorysnapshots_timestamp ON territorysnapshots (Timestamp);

CREATE TABLE IF NOT EXISTS snapshots (
    ID INTEGER PRIMARY KEY,
    playeronline BOOLEAN NOT NULL CHECK (playeronline IN (0, 1)),
    username TEXT,
    uuid TEXT NOT NULL,
    x INT,                              -- coords are NULL when the player isn't on the map
    y INT,
    z INT,
    yaw INT,
    Timestamp INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS snapshots_uuid_timestamp ON snapshots (uuid, Timestamp);
CREATE INDEX IF NOT EXISTS snapshots_timestamp ON snapshots (Timestamp);

CREATE TABLE IF NOT EXISTS apikeys (
    ID INTEGER PRIMARY KEY,
    createperms BOOLEAN NOT NULL CHECK (createperms IN (0, 1)),
    readperms BOOLEAN NOT NULL CHECK (readperms IN (0, 1)),
    deleteperms BOOLEAN NOT NULL CHECK (deleteperms IN (0, 1)),
    keyhash TEXT NOT NULL UNIQUE,       -- sha256 of the key, the key itself is never stored
    Timestamp INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
