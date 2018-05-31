# -*- coding: utf-8 -*-
import django_rq
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command


class SharedFoundationConfig(AppConfig):
    name = 'shared_foundation'

    def ready(self):
        scheduler = django_rq.get_scheduler('default')

        for job in scheduler.get_jobs():
            if "shared_foundation" in str(job):
                job.delete()
