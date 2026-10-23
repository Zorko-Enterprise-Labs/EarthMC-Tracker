import requests
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Configuration ----
# Minecraft coordinate bounds for the whole map:
MIN_X = -64702
MAX_X = 64702
MIN_Z = -32275
MAX_Z = 32275

DEFAULT_RATELIMIT_PROTECTION = False

# The zoom levels we want to download. 
# Leaflet map uses Zoom 0 (furthest out) to Zoom 5 (max zoom).
# ZOOM_LEVELS = [0, 1, 2, 3, 4, 5]
DEFAULT_ZOOM_LEVELS = [0,1,2,3,4,5]

# Seconds before giving up on a tile, so a stuck request can't block a worker forever
TILE_TIMEOUT = 15

def _download_tile(session, tile_url, file_path, count, total_tiles, tx, tz, zoom, RATELIMIT_PROTECTION, verboselogging=True):
    # Skip if already downloaded
    if os.path.exists(file_path):
        return

    try:
        res = session.get(tile_url, timeout=TILE_TIMEOUT)
    except requests.RequestException as e:
        # One failed tile shouldn't stop the whole download, it gets retried on the next run
        if verboselogging:
            print(f"[{count}/{total_tiles}] Failed {tx}_{tz}.png (Zoom {zoom}): {e}")
        return

    if res.status_code == 200:
        # Write to a temp file first, so an interrupted download never leaves a half-written
        # tile that would be skipped as "already downloaded" forever
        temp_path = file_path + ".part"
        with open(temp_path, 'wb') as f:
            f.write(res.content)
        os.replace(temp_path, file_path)
        if verboselogging:
            print(f"[{count}/{total_tiles}] Downloaded {tx}_{tz}.png (Zoom {zoom})")
    
    # Tiny sleep to ensure you don't get IP banned
    if RATELIMIT_PROTECTION: 
        time.sleep(0.1)

def download_all_tiles(output_folder, ZOOM_LEVELS=DEFAULT_ZOOM_LEVELS, RATELIMIT_PROTECTION=DEFAULT_RATELIMIT_PROTECTION, max_workers=30, verboselogging=True, status_callback=None):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    # requests only keeps 10 connections open by default, give every worker its own
    adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=max_workers)
    session.mount("https://", adapter)

    for zoom in ZOOM_LEVELS:
        status_msg = f"Downloading Zoom Level {zoom}..."
        if verboselogging:
            print(f"\n--- {status_msg} ---")
        
        if status_callback:
            status_callback(status_msg)

        out_dir = os.path.join(output_folder, str(zoom))
        os.makedirs(out_dir, exist_ok=True)
    
        # Calculate grid size for this specific zoom
        # EarthMC uses a squaremap which handles zoom mathematically.
        blocks_per_pixel = 2 ** (5 - zoom)
        blocks_per_tile = 512 * blocks_per_pixel
        
        min_tx = math.floor(MIN_X / blocks_per_tile)
        max_tx = math.floor(MAX_X / blocks_per_tile)
        min_tz = math.floor(MIN_Z / blocks_per_tile)
        max_tz = math.floor(MAX_Z / blocks_per_tile)
        
        total_tiles = (max_tx - min_tx + 1) * (max_tz - min_tz + 1)
        if verboselogging:
            print(f"Total grid tiles to check for zoom {zoom}: {total_tiles}")
        
        count = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for tz in range(min_tz, max_tz + 1):
                for tx in range(min_tx, max_tx + 1):
                    count += 1
                    tile_url = f"https://map.earthmc.net/tiles/minecraft_overworld/{zoom}/{tx}_{tz}.png"
                    file_path = os.path.join(out_dir, f"{tx}_{tz}.png")
                    
                    futures.append(executor.submit(
                        _download_tile, session, tile_url, file_path, count, total_tiles, tx, tz, zoom, RATELIMIT_PROTECTION, verboselogging
                    ))
            
            for future in as_completed(futures):
                future.result()
    if verboselogging:
        print("\nDone downloading all tiles!")

if __name__ == "__main__":
    download_all_tiles("test/", ZOOM_LEVELS=[1])
