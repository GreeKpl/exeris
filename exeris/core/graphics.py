import io
from PIL import ImageDraw
from shapely.geometry import Polygon, Point

from PIL import Image
from exeris.core.main import db
from exeris.core import models

MAP_PER_PX = 100

VIEW_SIZE = 500

COLORS = {"grass": "green", "water": "blue", "sea": "blue", "road": "brown"}


def get_map():
    im = Image.new("RGB", (500, 500), "white")

    terrains = models.TerrainArea.query.order_by(models.TerrainArea.priority.asc()).all()
    draw = ImageDraw.Draw(im)
    for t in terrains:
        coords = t.terrain.exterior.coords[:-1]
        coords = [(c * MAP_PER_PX, d * MAP_PER_PX) for c, d in coords]
        print(coords, COLORS[t.type_name])
        draw.polygon(coords, fill=COLORS[t.type_name])
        # im.paste(black, (int(pos[0] * MAP_PER_PX), int(pos[1] * MAP_PER_PX)))

    root_locs = models.RootLocation.query.all()

    for rl in root_locs:
        p = rl.position.coords[0]
        low = (p[0] - 0.05) * MAP_PER_PX, (p[1] - 0.05) * MAP_PER_PX
        upp = (p[0] + 0.05) * MAP_PER_PX, (p[1] + 0.05) * MAP_PER_PX

        draw.pieslice([low, upp], 0, 360, fill="black")

    del draw

    b = io.BytesIO()
    im.save(b, 'png')
    return b.getvalue()
