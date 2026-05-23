DROP TABLE IF EXISTS snapshots;
DROP TABLE IF EXISTS apikeys;

CREATE TABLE snapshots (
    ID INTEGER PRIMARY KEY,
    playeronline BOOLEAN,
    uuid TEXT NOT NULL,
    x INT,
    y INT,
    z INT,
    yaw INT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE apikeys (
    ID INTEGER PRIMARY KEY,
    createperms BOOLEAN NOT NULL,
    readperms BOOLEAN NOT NULL,
    deleteperms BOOLEAN NOT NULL,
    apikey TEXT NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)