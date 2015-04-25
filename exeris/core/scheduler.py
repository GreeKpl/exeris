import time
from shapely.geometry import Point

from config import DevelopmentConfig
from exeris.core.main import db, create_app
from exeris.core.models import RootLocation

from util import create_db

__author__ = 'alek'


class Scheduler:

    def check_new_tasks(self):
        return 0

    def pop_task(self):
        return TravelProcess()

    def process_task(self, task):
        db.session.rollback()  # force finishing previous transaction
        tries = 0
        while tries < 3:
            try:
                tries += 1
                task.run()
                db.session.commit()
                return True
            except Exception as e:
                print(e)
                raise
                db.session.rollback()
        if tries > 1:
            print("SEND WARNING")
        print("SEND EMAIL WITH ERROR")
        return False


class Process:

    def run(self):
        pass


class TravelProcess(Process):

    def run(self):
        mobile_locs = RootLocation.query.filter_by(is_mobile=True).all()
        for loc in mobile_locs:
            pos = loc.position
            point = Point(pos.x + 1, pos.y + 1)
            loc.position = point

scheduler = Scheduler()
flask_app = create_app()


with flask_app.app_context():

    while True:
        try:
            task = scheduler.pop_task()
            if task:
                scheduler.process_task(task)
            else:
                found_tasks = scheduler.check_new_tasks()

                if not found_tasks:
                    time.sleep(1)
        except Exception as e:
            print("SOMETHING BAD HAS HAPPENED", e)  # e.g. database connection failed
            print("TRYING AGAIN!!!")
            raise


