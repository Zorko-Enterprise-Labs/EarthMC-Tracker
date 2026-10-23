# EarthMC Tracker (codename: Samaritan)

> **Status: archived.** The project stopped in May 2026 and is kept here in a runnable state. See [Unfinished](#unfinished) if you want to pick it back up.

A player tracker for the **EarthMC** Minecraft server, inspired by "The Machine" / Samaritan from *Person of Interest*. It was built as an unofficial side project for a nation's "national security program": pick players, see where they are live on the map, and keep a history of where they've been.

Everything it tracks is **in-game data from public sources**:

- `map.earthmc.net/tiles/players.json`: live player positions shown on the public EarthMC map
- `api.earthmc.net/v4`: online status
- `api.mojang.com`: username → UUID lookups
- `map.earthmc.net/tiles/...`: map tile images

It never ran long-term or publicly. It was only ever run locally.

## What works

- **Live map** (`/`): EarthMC's map with every visible player drawn live, refreshed every 3 seconds, plus search with autocomplete.
- **Player snapshots**: record one player's position (`track`) or every online player at once (`fullsnapshot`), then query them by player, ID or time.
- **Map snapshots**: download a full copy of the map's tiles (20 parallel workers) so you can view the map as it was at that time.
- **API keys** with separate create/read/delete permissions. Only SHA-256 hashes are stored.

## Running it

Needs Python 3.9+.

```bash
git clone https://github.com/NejcZorko007/EarthMC-Tracker.git
cd EarthMC-Tracker
pip install -r requirements.txt
python server.py
```

Then open http://127.0.0.1:5000.

`server.py` runs the API and also downloads the live map tiles into `tiles/` in the background (about 42,000 images the first time; after that only missing ones). To run just the API without the downloader, use `python api.py` (or `runapi.cmd` / `runapi.sh`).

The database (`database.db`) is created and upgraded automatically on startup. It's safe to start with an existing one, and nothing is ever dropped.

### API keys

```bash
python apikeys.py --create --read --delete
```

The key is printed once and can't be recovered from the database afterwards. The web map uses the key hard-coded at the top of `templates/index.html`, so the server is meant to stay on `127.0.0.1`.

## API

All `POST` endpoints take JSON with an `apikey`. Errors look like `{"error": "...", "errorcode": n}` with a matching HTTP status (see `errors.py`). Timestamps are unix seconds (UTC). UUIDs can be sent dashed or undashed and are stored undashed.

| Endpoint | Permission | Body / params |
| --- | --- | --- |
| `POST /players/takesnapshot` | create | `action: "track"` + `uuid`, or `action: "fullsnapshot"` |
| `POST /players/getsnapshots` | read | optional `id`, or `uuid` and/or `timestamp` + `timeradius` (seconds, default 3) |
| `POST /players/deletesnapshot` | delete | `snapshotids: [..]` (all or nothing) |
| `GET /players/liveplayers` | – | live overworld players |
| `GET /players/search?username=` | – | find an online player by name |
| `POST /map/createsnapshot` | create | optional `zoomlevels: [0..5]`, downloads in the background |
| `POST /map/getsnapshots` | read | optional `id`. `available` says whether the tiles are on this computer |
| `GET or POST /map/gettiles` | read | `snapshotid`, `zoomlevel`, `tile` (e.g. `104_18`), returns a PNG |
| `POST /map/deletesnapshots` | delete | `snapshotids: [..]` (deletes the database rows, not the tile files) |

## Layout

| Path | What it is |
| --- | --- |
| `api.py` | Flask app with all the endpoints above |
| `server.py` | Runs the API and the background tile downloader together |
| `sql.py`, `schema.sql` | Database access, schema and automatic migrations |
| `apikeys.py`, `errors.py` | API keys (and a small CLI to create them), error codes |
| `players/api_interface.py` | EarthMC / Mojang API calls |
| `map/` | Tile downloader (`map.py`) and map snapshot folders (`api_interface.py`) |
| `templates/index.html` | The web map (Leaflet) |

`tiles/` and `maptiles/` hold downloaded images and aren't in git. A map snapshot made on one computer has no tiles on another.

## Unfinished

What was planned but never built, roughly in order of usefulness:

1. **Watchlist**: a table of the players under watch. Right now every snapshot has to be requested by hand.
2. **Automatic tracking**: a background job that snapshots the watchlist every minute or so.
3. **History view**: select a player on the map and see their recorded positions as a trail, or scrub through time.
4. **Territory snapshots**: the `territorysnapshots` table and its functions in `sql.py` exist, but nothing fills them or exposes them through the API.
5. **Coordinate filter**: search snapshots by area as well as by time (`REMEMBER TO ADD COORDINATE RADIUS THING` in `api.py`).
