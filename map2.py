import requests
from PIL import Image
import io

zoom = 1
x, z = 53784, 
tile_url = f"https://map.earthmc.net/tiles/minecraft_overworld/{zoom}/{x}_{z}.png"

headers = {"User-Agent": "Mozilla/5.0"}
res = requests.get(tile_url, headers=headers)

if res.status_code == 200:
    img = Image.open(io.BytesIO(res.content))
    img.show()
else:
    print(f"Failed to retrieve tile: {res.status_code}")