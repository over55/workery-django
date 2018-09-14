# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime, timedelta
from dateutil import tz
from decimal import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Sum
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command
from shared_foundation.models.franchise import SharedFranchise
from shared_foundation.models.franchise import SharedFranchiseDomain
from tenant_foundation.constants import *
from tenant_foundation.models import AwayLog


class Command(BaseCommand): #TODO: UNIT TEST
    """
    python manage.py update_away_logs
    """
    help = _('ETL will iterate through all away logs in all tenants and close them if it is past the return date.')

    def handle(self, *args, **options):
        franchises = SharedFranchise.objects.filter(
            ~Q(schema_name="public") &
            ~Q(schema_name="test")
        )
        for franchise in franchises.all():
            # Connection needs first to be at the public schema, as this is where
            # the database needs to be set before creating a new tenant. If this is
            # not done then django-tenants will raise a "Can't create tenant outside
            # the public schema." error.
            connection.set_schema_to_public() # Switch to Public.

            # Connection will set it back to our tenant.
            connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

            # Run the command which exists in the franchise.
            self.run_update_away_logs_for_franchise(franchise)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated all away logs.'))
        )

    def run_update_away_logs_for_franchise(self, franchise):
        """
        Function will iterate through all the `running` away logs and
        perform the necessary operations.
        """
        tenant_todays_date = franchise.get_todays_date_plus_days()
        away_logs = AwayLog.objects.filter(until_date__gte=tenant_todays_date).order_by('-id')
        for away_log in away_logs.iterator():
            self.stdout.write(
                self.style.SUCCESS(
                    _('Deleted away logs ID #%(id)s.' % {
                        'id': str(away_log.id)
                    })
                )
            )
            away_log.delete()
