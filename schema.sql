DROP TABLE IF EXISTS mapsnapshots;
DROP TABLE IF EXISTS territorysnapshots;
DROP TABLE IF EXISTS snapshots;
-- DROP TABLE IF EXISTS apikeys;

CREATE TABLE mapsnapshots (
    ID INTEGER PRIMARY KEY,
    folderpath TEXT NOT NULL,
    completed BOOLEAN NOT NULL,
    Timestamp INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE TABLE territorysnapshots (
    ID INTEGER PRIMARY KEY,
    -- POINTS SHOULD BE A JSON ARRAY SAVED AS A STRING
    points TEXT NOT NULL, 
    townname TEXT NOT NULL,
    nation TEXT NOT NULL,
    townboard TEXT NOT NULL,
    iscapital BOOLEAN NOT NULL,
    mapcolour TEXT NOT NULL,
    Timestamp INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE TABLE snapshots (
    ID INTEGER PRIMARY KEY,
    playeronline BOOLEAN,
    uuid TEXT NOT NULL,
    x INT,
    y INT,
    z INT,
    yaw INT,
    Timestamp INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

-- CREATE TABLE apikeys (
--     ID INTEGER PRIMARY KEY,
--     createperms BOOLEAN NOT NULL,
--     readperms BOOLEAN NOT NULL,
--     deleteperms BOOLEAN NOT NULL,
--     apikey TEXT NOT NULL,
--     Timestamp INTEGER NOT NULL DEFAULT (strftime('%s','now'))
-- );