# -*- coding: utf-8 -*-
import django_rq
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command


def run_update_ongoing_orders_func():
    call_command('update_ongoing_orders', verbosity=0)


def run_update_away_logs_func():
    call_command('update_away_logs', verbosity=0)


def run_update_expired_associates_func():
    call_command('update_expired_associates', verbosity=0)


class SharedEtlConfig(AppConfig):
    """
    Class initializes our extract transform and load (ETL) scripts on django the
    runtime of the application. The ETLs are managed by the `rq-scheduler
    code which will load into `redis` background task to process.
    """
    name = 'shared_etl'
    verbose_name = 'Shared Extract Transform & Loads (ETLs)'

    def ready(self):
        """
        On django runtime, load up the following code.
        """
        scheduler = django_rq.get_scheduler('default')

        # Delete previously loaded ETLs.
        for job in scheduler.get_jobs():
            if "shared_etl" in str(job): # Only delete jobs belonging to this app.
                job.delete()

        # Variable used to track the maximum number of minutes the ETL can
        # run before it's considered an error and needs to stop the ETL.
        timeout = timedelta(minutes=666)

        scheduler.cron(
            "0 0 1 * *",                             # A cron string - Run every 12:00AM on the FIRST day of every month
            func=run_update_ongoing_orders_func,     # Function to be queued
            repeat=None,                             # Repeat this number of times (None means repeat forever)
            timeout=timeout.seconds                  # Automatically terminate process if exceeds this time.
        )
        scheduler.cron(
            "0 0 L * *",                             # A cron string - Run every 12:00AM on the LAST day of every month
            func=run_update_ongoing_orders_func,     # Function to be queued
            repeat=None,                             # Repeat this number of times (None means repeat forever)
            timeout=timeout.seconds                  # Automatically terminate process if exceeds this time.
        )
        scheduler.cron(
            "1 0 * * *",                             # A cron string - Run every 12:00AM every day.
            func=run_update_away_logs_func,          # Function to be queued
            repeat=None,                             # Repeat this number of times (None means repeat forever)
            timeout=timeout.seconds                  # Automatically terminate process if exceeds this time.
        )
        scheduler.cron(
            "1 0 * * *",                             # A cron string - Run every 12:00AM every day.
            func=run_update_expired_associates_func, # Function to be queued
            repeat=None,                             # Repeat this number of times (None means repeat forever)
            timeout=timeout.seconds                  # Automatically terminate process if exceeds this time.
        )
