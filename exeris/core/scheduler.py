import logging
import time

from exeris.core import models, deferred, general
from exeris.core.main import db
# noinspection PyUnresolvedReferences
from exeris.extra import hooks


class Scheduler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def run(self):
        while True:
            self._start_transaction()
            self.run_iteration()
            self._commit_transaction()

    def run_iteration(self):
        self.logger.info("Starting another iteration")
        try:
            task = self.pop_task()
            if task:
                self.logger.info("### Running task %s", task.process_data)

                self.process_task(task)

                if task.is_repeatable():  # it should be kept in the database to be used again
                    self.update_next_execution_time(task)
                else:
                    db.session.delete(task)
                    self.logger.info("Task deleted")
            else:
                self.logger.info("No tasks found. Going to sleep")
                time.sleep(1)
        except Exception as e:
            self.logger.error("Unable to complete task. End of work", e)

    def pop_task(self):
        current_timestamp = general.GameDate.now().game_timestamp

        self.logger.debug("current game timestamp: " + str(current_timestamp))

        return models.ScheduledTask.query.filter(models.ScheduledTask.execution_game_timestamp <= current_timestamp) \
            .order_by(models.ScheduledTask.execution_game_timestamp).first()

    def process_task(self, task):
        tries = 0
        self.logger.info("Trying to run task process: %s", task.process_data)
        process = deferred.call(task.process_data, task=task)
        while tries < 3:
            try:
                self._start_transaction()  # force finishing previous transaction
                tries += 1
                process.perform()

                self._commit_transaction()
                self.logger.info("Task executed successfully: %s", task.process_data)
                return True
            except Exception as e:
                self.logger.warn("Failed to run process for the %s time: %s,", tries, task.process_data, exc_info=True)
                self._rollback_transaction()
        self.logger.error("UNABLE TO COMPLETE PROCESS %s", task.process_data)
        return False

    def update_next_execution_time(self, task):
        if task.execution_game_timestamp + 10 < general.GameDate.now().game_timestamp:  # TODO temporary change to avoid multiple runs at once
            task.execution_game_timestamp = general.GameDate.now().game_timestamp
        task.execution_game_timestamp += task.execution_interval
        self.logger.info("Task will be run again at %s", task.execution_game_timestamp)

    def _start_transaction(self):
        db.session.rollback()

    def _commit_transaction(self):
        db.session.commit()

    def _rollback_transaction(self):
        db.session.rollback()
