import logging
import time

from exeris.core.main import db
from exeris.core import models, deferred

__author__ = 'alek'


class Scheduler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def pop_task(self):
        return models.ScheduledTask.query.order_by(models.ScheduledTask.execution_game_date).first()

    def process_task(self, task):
        tries = 0
        self.logger.info("Trying to run task process: %s", task.process_data)
        process = deferred.call(task.process_data)
        while tries < 3:
            try:
                self._start_transaction()  # force finishing previous transaction
                tries += 1
                process.perform()

                return True
            except Exception as e:
                self.logger.warn("Failed to run process for the %s time: %s,", tries, task.process_data, exc_info=True)
                self._rollback_transaction()
        self.logger.error("UNABLE TO COMPLETE PROCESS %s", task.process_data)
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

    def _start_transaction(self):
        db.session.rollback()

    def _commit_transaction(self):
        db.session.commit()

    def _rollback_transaction(self):
        db.session.rollback()