import requests
import math
import os


ZOOM_LEVEL = 3
OUTPUT_DIR = f"tiles/minecraft_overworld/{ZOOM_LEVEL}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MIN_X_BLOCK = -64702
MAX_X_BLOCK = 64702
MIN_Z_BLOCK = -32275
MAX_Z_BLOCK = 32275

TILE_SIZE_PX = 512
BLOCKS_PER_PIXEL = 2 ** (5 - ZOOM_LEVEL)
BLOCKS_PER_TILE = TILE_SIZE_PX * BLOCKS_PER_PIXEL

min_tile_x = math.floor(MIN_X_BLOCK / BLOCKS_PER_TILE)
max_tile_x = math.floor(MAX_X_BLOCK / BLOCKS_PER_TILE)
min_tile_z = math.floor(MIN_Z_BLOCK / BLOCKS_PER_TILE)
max_tile_z = math.floor(MAX_Z_BLOCK / BLOCKS_PER_TILE)

print(f"Blocks per Tile: {BLOCKS_PER_TILE} x {BLOCKS_PER_TILE}")
print(f"Required Tile X range: {min_tile_x} to {max_tile_x}")
print(f"Required Tile Z range: {min_tile_z} to {max_tile_z}")

width_tiles = max_tile_x - min_tile_x + 1
height_tiles = max_tile_z - min_tile_z + 1
print(f"Total tiles to download: {width_tiles * height_tiles}")

headers = {"User-Agent": "Mozilla/5.0"}
session = requests.Session()

for tz in range(min_tile_z, max_tile_z + 1):
    for tx in range(min_tile_x, max_tile_x + 1):
        tile_url = f"https://map.earthmc.net/tiles/minecraft_overworld/{ZOOM_LEVEL}/{tx}_{tz}.png"
        file_path = os.path.join(OUTPUT_DIR, f"{tx}_{tz}.png")
        if os.path.exists(file_path):
            print(f"Tile {tx}_{tz} already exists, skipping")
            continue
        res = session.get(tile_url, headers=headers)
        if res.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(res.content)
            print(f"Downloaded tile {tx}_{tz}")
        else:
            print(f"Tile {tx}_{tz} not found (empty ocean)")

print("Done downloading all tiles!")

