import io

from PIL import Image
from PIL import ImageDraw

from exeris.core import models

MAP_PER_PX = 50

VIEW_SIZE = 500

COLORS = {"grassland": "green", "grassland_coast": "#4CBB17",
          "deep_water": "#1F75cE", "shallow_water": "#40a3cF",
          "road": "brown", "forest": "darkgreen",
          }


def transpose(y):
    return VIEW_SIZE - y


def get_map(character=None):
    im = Image.new("RGB", (VIEW_SIZE, VIEW_SIZE), "white")

    terrains = models.TerrainArea.query.order_by(models.TerrainArea.priority.asc()).all()
    draw = ImageDraw.Draw(im)
    for t in terrains:
        coords = t.terrain.exterior.coords[:-1]
        coords = [(x * MAP_PER_PX, transpose(y * MAP_PER_PX)) for x, y in coords]

        draw.polygon(coords, fill=COLORS[t.type_name])
        # im.paste(black, (int(pos[0] * MAP_PER_PX), int(pos[1] * MAP_PER_PX)))

    root_locs = models.RootLocation.query.all()

    for rl in root_locs:
        p = rl.position.coords[0]
        low = (p[0] - 0.05) * MAP_PER_PX, transpose((p[1] + 0.05) * MAP_PER_PX)
        upp = (p[0] + 0.05) * MAP_PER_PX, transpose((p[1] - 0.05) * MAP_PER_PX)

        draw.pieslice([low, upp], 0, 360, fill="black")

    if character:
        p = character.get_position().coords[0]
        low = (p[0] - 0.05) * MAP_PER_PX, transpose((p[1] + 0.05) * MAP_PER_PX)
        upp = (p[0] + 0.05) * MAP_PER_PX, transpose((p[1] - 0.05) * MAP_PER_PX)

        draw.pieslice([low, upp], 0, 360, fill="red")

    del draw

    b = io.BytesIO()
    im.save(b, 'png')
    return b.getvalue()
