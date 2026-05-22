import requests
from PIL import Image
import io
import math

# The specific Minecraft block coordinates you want to see
block_x = 53784
block_z = 10160  # Added a Z coordinate

zoom = 5

# 1. Calculate how many blocks fit in a single 512x512 tile at this zoom
blocks_per_pixel = 2 ** (5 - zoom)
blocks_per_tile = 512 * blocks_per_pixel

# 2. Divide block coords by blocks per tile to get the exact tile grid index
tile_x = math.floor(block_x / blocks_per_tile)
tile_z = math.floor(block_z / blocks_per_tile)

print(f"Block X:{block_x}, Z:{block_z} is located in tile {tile_x}_{tile_z}.png (Zoom {zoom})")

# 3. Fetch that specific tile
tile_url = f"https://map.earthmc.net/tiles/minecraft_overworld/{zoom}/{tile_x}_{tile_z}.png"

headers = {"User-Agent": "Mozilla/5.0"}
res = requests.get(tile_url, headers=headers)

if res.status_code == 200:
    img = Image.open(io.BytesIO(res.content))
    img.show()
else:
    print(f"Failed to retrieve tile: {res.status_code}")