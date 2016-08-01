"""This module schedules all the periodic batch processes on heroku.

https://devcenter.heroku.com/articles/clock-processes-python
"""
import logging

# Use the default import to avoid module AttributeError (http://goo.gl/YM7kyZ)
from apscheduler.schedulers.blocking import BlockingScheduler

import ufo
from ufo.services import key_distributor
from ufo.services import user_synchronizer


# http://stackoverflow.com/questions/28724459/no-handlers-could-be-found-for-logger-apscheduler-executors-default
logging.basicConfig()

SCHEDULER = BlockingScheduler()

@SCHEDULER.scheduled_job('interval', minutes=2)
def schedule_user_key_distribution():
  """Schedule the user key distribution to proxy servers."""
  ufo.app.logger.info('Scheduling key distribution to proxy server.')
  key_distributor_service = key_distributor.KeyDistributor()
  key_distributor_service.enqueue_key_distribution_jobs()

@SCHEDULER.scheduled_job('interval', minutes=15)
def schedule_user_sync():
  """Schedule the user sync job."""
  ufo.app.logger.info('Scheduling user sync.')
  user_sync_service = user_synchronizer.UserSynchronizer()
  user_sync_service.enqueue_user_sync()


SCHEDULER.start()
