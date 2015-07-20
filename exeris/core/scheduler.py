import base64
import logging
import time

from shapely.geometry import Point

from exeris.core.main import db
from exeris.core import models, deferred


__author__ = 'alek'


class Scheduler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def pop_task(self):
        return models.ScheduledTask.query.order_by(models.ScheduledTask.execution_game_date).first()

    def process_task(self, task):
        #db.session.rollback()  # force finishing previous transaction
        tries = 0
        self.logger.info("Trying to run task process: %s", base64.decodebytes(task.process_data))
        process = deferred.call(task.process_data)
        while tries < 3:
            try:
                tries += 1
                process.run()
                #db.session.commit()
                return True
            except Exception as e:
                self.logger.warn("Failed to run process for the %s time: %s,", tries, base64.decodebytes(task.process_data), exc_info=True)
                #db.session.rollback()
        self.logger.error("UNABLE TO COMPLETE PROCESS %s", base64.decodebytes(task.process_data))
        return False

    def run(self):
        while True:
            self.run_iteration()
            db.session.commit()

    def run_iteration(self):
        try:
            task = self.pop_task()
            if task:
                self.process_task(task)

                if task.is_repeatable():  # it should be kept in the database to be used again
                    task.execution_game_date += task.execution_interval
                else:
                    db.session.delete(task)
            else:
                time.sleep(1)
        except Exception as e:
            self.logger.error("Unable to complete task. Running another iteration", e)


class Process:

    def run(self):
        pass


class TravelProcess(Process):

    def __init__(self):
        pass

    def run(self):
        mobile_locs = models.RootLocation.query.filter_by(is_mobile=True).all()
        for loc in mobile_locs:
            pos = loc.position
            point = Point(pos.x + 1, pos.y + 1)
            loc.position = point


class ActivityProcess(Process):

    def __init__(self):
        pass

    def run(self):
        activities = models.Activity.query.all()
        for activity in activities:
            self.make_progress(activity)

    def make_progress(self, activity):
        print("progress of ", activity)
        workers = models.Character.query.filter(models.Character.activity==activity).all()
        for worker in workers:
            print("worker ", worker)
            if "tools" in activity.requirements:
                if self.check_tool_requirements(worker, activity.requirements["tools"]):
                    print("TOOLS OK")
            if self.check_proximity(worker, activity):
                print("PROXIMITY OK")
            if "input" in activity.requirements:
                for material in activity.requirements["input"]:
                    if material["left"] > 0:
                        print("fail input req")

            activity.ticks_left -= 1

        if activity.ticks_left <= 0:
            self.finish_activity(activity)

    def check_tool_requirements(self, worker, tools):
        for tool_type_name in tools:
            item_type = models.ItemType.by_name(tool_type_name)

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
        print("finishing activity")
        for serialized_action in activity.result_actions:
            action = deferred.call(serialized_action, activity=activity, initiator=activity.initiator)
            action.perform()
