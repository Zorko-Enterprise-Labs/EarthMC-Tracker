import requests
import math
import os
import time

# --- Configuration ----
# Minecraft coordinate bounds
MIN_X = -64702
MAX_X = 64702
MIN_Z = -32275
MAX_Z = 32275

RATELIMIT_PROTECTION = False

# The zoom levels we want to download. 
# Leaflet map uses Zoom 0 (furthest out) to Zoom 5 (max zoom).
# ZOOM_LEVELS = [0, 1, 2, 3, 4, 5]
ZOOM_LEVELS = [0,1,2,3,4]

def download_all_tiles():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    for zoom in ZOOM_LEVELS:
        print(f"\n--- Downloading Zoom Level {zoom} ---")
        out_dir = f"tiles/minecraft_overworld/{zoom}"
        os.makedirs(out_dir, exist_ok=True)
    
        # Calculate grid size for this specific zoom
        blocks_per_pixel = 2 ** (5 - zoom)
        blocks_per_tile = 512 * blocks_per_pixel
        
        min_tx = math.floor(MIN_X / blocks_per_tile)
        max_tx = math.floor(MAX_X / blocks_per_tile)
        min_tz = math.floor(MIN_Z / blocks_per_tile)
        max_tz = math.floor(MAX_Z / blocks_per_tile)
        
        total_tiles = (max_tx - min_tx + 1) * (max_tz - min_tz + 1)
        print(f"Total grid tiles to check for zoom {zoom}: {total_tiles}")
        
        count = 0
        for tz in range(min_tz, max_tz + 1):
            for tx in range(min_tx, max_tx + 1):
                count += 1
                tile_url = f"https://map.earthmc.net/tiles/minecraft_overworld/{zoom}/{tx}_{tz}.png"
                file_path = os.path.join(out_dir, f"{tx}_{tz}.png")
                
                # Skip if already downloaded
                if os.path.exists(file_path):
                    # print(f"[{count}/{total_tiles}] Zoom {zoom} Tile {tx}_{tz} already exists, skipping")
                    continue
                    
                res = session.get(tile_url)
                
                if res.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(res.content)
                    print(f"[{count}/{total_tiles}] Downloaded {tx}_{tz}.png")
                # else:
                #     pass # Silenced to prevent terminal spam when tiles are empty (ocean)
                
                # Tiny sleep to ensure you don't get IP banned
                if RATELIMIT_PROTECTION: 
                    time.sleep(0.1)

    print("\nDone downloading all tiles!")

if __name__ == "__main__":
    download_all_tiles()
