#!/usr/bin/env python3
from exeris.core import general, models

from exeris.core.main import create_app, db

import exeris.core.scheduler as scheduler
__author__ = 'alek'


app = create_app()

with app.app_context():
    db.create_all()

    if not models.ScheduledTask.query.count():
        hunger_task = models.ScheduledTask(["exeris.core.actions.ActivitiesProgressProcess", {}], general.GameDate.now().game_timestamp, 20)
        activity_task = models.ScheduledTask(["exeris.core.actions.HungerProcess", {}], general.GameDate.now().game_timestamp, 20)
        db.session.add_all([hunger_task, activity_task])
        db.session.commit()

    scheduler.Scheduler().run()
