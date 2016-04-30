#!/usr/bin/env python3
from exeris.core import general, models

from exeris.core.main import create_app, db

import exeris.core.scheduler as scheduler

app = create_app()

with app.app_context():
    db.create_all()

    if not models.ScheduledTask.query.count():
        activity_task = models.ScheduledTask(["exeris.core.actions.WorkProcess", {}],
                                             general.GameDate.now().game_timestamp, 5)
        db.session.add(activity_task)
        # eating_task = models.ScheduledTask(["exeris.core.actions.EatingProcess", {}], general.GameDate.now().game_timestamp, 20)
        # db.session.add(eating_task)

        db.session.commit()

    scheduler.Scheduler().run()
