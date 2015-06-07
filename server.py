#!/usr/bin/env python3

from exeris.core.main import create_app, db
import exeris.core.scheduler as scheduler
__author__ = 'alek'


app = create_app()

with app.app_context():
    db.create_all()
    scheduler.Scheduler().run()
