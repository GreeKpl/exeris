from PIL import ImageDraw
from shapely.geometry import Polygon, Point
from util.create_db import create_db

__author__ = 'aleksander'

from PIL import Image
from exeris.core.main import db, create_app
from exeris.core import models

MAP_PER_PX = 100

VIEW_SIZE = 500

app = create_app()
create_db()

COLORS = ["red", "green", "yellow", "brown"]

with app.app_context():
    tt1 = models.TerrainType("grass", 1)
    tt2 = models.TerrainType("water", 2)
    road_type = models.TerrainType("road", 3)
    db.session.add_all([tt1, tt2])

    poly1 = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
    poly2 = Polygon([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])
    poly3 = Polygon([(1, 1), (5, 1), (5, 3), (3, 5), (1, 1)])
    poly4 = Polygon([(1, 1), (0.9, 1.1), (3.9, 4.1), (4, 4), (1, 1)])


    t1 = models.TerrainArea(poly1, tt1)
    t2 = models.TerrainArea(poly2, tt2)
    t3 = models.TerrainArea(poly3, tt1)
    road = models.TerrainArea(poly4, road_type)

    db.session.add_all([t1, t2, t3, road])

    rl1 = models.RootLocation(Point(1, 0), False, 304)
    rl2 = models.RootLocation(Point(2, 3), False, 30)
    rl3 = models.RootLocation(Point(4, 1), False, 71)
    rl4 = models.RootLocation(Point(5, 2), False, 71)

    db.session.add_all([rl1, rl2, rl3, rl4])

    db.session.flush()

    im = Image.new("RGB", (500, 500), "white")

    #print(ResultantTerrainArea.query.all())

    terrains = models.TerrainArea.query.all()
    draw = ImageDraw.Draw(im)
    for t in terrains:
        coords = t.terrain.exterior.coords[:-1]
        coords = [(c * MAP_PER_PX, d * MAP_PER_PX) for c, d in coords]
        print(coords, COLORS[t.terrain_type.color])
        draw.polygon(coords, fill=COLORS[t.terrain_type.color])
        # im.paste(black, (int(pos[0] * MAP_PER_PX), int(pos[1] * MAP_PER_PX)))

    root_locs = models.RootLocation.query.all()

    for rl in root_locs:
        p = rl.position.coords[0]
        low = (p[0] - 0.05) * MAP_PER_PX, (p[1] - 0.05) * MAP_PER_PX
        upp = (p[0] + 0.05) * MAP_PER_PX, (p[1] + 0.05) * MAP_PER_PX
        print([low, upp])
        draw.pieslice([low, upp], 0, 360, fill="black")

    del draw
    print("saving")
    im.save("hehe.png")
