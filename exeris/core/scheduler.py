import logging
from shapely.geometry import Point

from exeris.core.main import db
from exeris.core import models, deferred


__author__ = 'alek'


class Scheduler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def check_new_tasks(self):
        return 0

    def pop_task(self):
        return ActivityProcess()

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
        mobile_locs = models.RootLocation.query.filter_by(is_mobile=True).all()
        for loc in mobile_locs:
            pos = loc.position
            point = Point(pos.x + 1, pos.y + 1)
            loc.position = point


class ActivityProcess(Process):

    def run(self):
        activities = models.Activity.query.all()
        for activity in activities:
            self.make_progress(activity)

    def make_progress(self, activity):
        print("progress of ", activity)
        workers = models.Character.query.filter_by(activity=activity).all()
        for worker in workers:
            print("worker ", worker)
            if "tools" in activity.requirements:
                if self.check_tool_requirements(worker, activity.requirements["tools"]):
                    print("TOOLS OK")
            if self.check_proximity(worker, activity):
                print("PROXIMITY OK")

            activity.ticks_left -= 1

        if activity.ticks_left <= 0:
            self.finish_activity(activity)

    def check_tool_requirements(self, worker, tools):
        for tool_type_id in tools:
            item_type = models.ItemType.by_id(tool_type_id)

            if not models.Item.query.filter_by(type=item_type).filter(models.Item.is_in(worker)).count():
                return False
            return True

    def check_proximity(self, worker, activity):
        print(worker.being_in)
        print(activity.being_in)
        if worker.being_in != activity.being_in.being_in:
            return False
        return True

    def finish_activity(self, activity):
        for serialized_action in activity.result_actions:
            action = deferred.call(serialized_action)
            action.perform()


'''

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

'''
