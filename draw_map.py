#!/usr/bin/env python3

import exeris.core.graphics as graphics
from exeris.core.main import create_app
from util.create_db import create_db


app = create_app()
create_db()

with app.app_context():
    graphics.get_map().save("map.png")
