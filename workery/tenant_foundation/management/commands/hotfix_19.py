# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import parser
from freezegun import freeze_time
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _

from shared_foundation import constants
from shared_foundation.models import (
    SharedUser,
    SharedFranchise
)
from tenant_foundation.models import (
    Associate,
    # Comment,
    Customer,
    InsuranceRequirement,
    Organization,
    WorkOrder,
    # WorkOrderComment,
    WorkOrderServiceFee,
    ResourceCategory,
    ResourceItem,
    ResourceItemSortOrder,
    SkillSet,
    Staff,
    Tag,
    VehicleType,
    AwayLog
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will run `hotfix_19`.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_19 "london"
        """
        parser.add_argument('schema_name', nargs='+', type=str)

    def process_away_log(self, away_log, now_d):
        # Policy check expired.
        associate = away_log.associate
        police_check_d = associate.police_check

        if police_check_d:
            # CASE 1 OF 3: POLICE CHECK HAS EXPIRED.
            if police_check_d <= now_d:
                self.stdout.write(
                    self.style.WARNING(_('Associate #%(id)s policy check of %(dt) has expired as of today %(dt_fin)s.')%{
                        'id': str(associate.id),
                        'dt': str(police_check_d),
                        'dt_fin': str(now_d)
                    })
                )
                away_log.reason = 5
                away_log.save()

            # CASE 2 OF 3: POLICE CHECK HAS NOT EXPIRED.
            else:
                self.stdout.write(
                    self.style.SUCCESS(_('Associate #%(id)s has police check which has not expired.')%{
                        'id': str(associate.id)
                    })
                )
        # CASE 3 OF 3: NO POLICE CHECK SPECIFIED! (VERY BAD!)
        else:
            self.stdout.write(
                self.style.ERROR(_('Associate #%(id)s has no police check.')%{
                    'id': str(associate.id)
                })
            )
            away_log.reason = 5
            away_log.save()

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.
        # Get the user inputs.
        schema_name = options['schema_name'][0]

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)

            # Get the current date for this particular franchise.
            now_dt = franchise.get_todays_date_plus_days()
            now_d = now_dt.date()
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

        #----------------------------------------------------------------------#
        # ALGORITHM:
        # WE WANT TO FREEZE TIME TO THE `LAST_MODIFIED` DATETIME SO THE RECORD
        # DOES NOT LOOKED LIKE IT WAS MODIFIED. SPECIAL THANKS TO LINK:
        # https://stackoverflow.com/a/40423482
        #----------------------------------------------------------------------#
        start_dt = parser.parse("2019-06-22")
        for away_log in AwayLog.objects.filter(reason=4, start_date__gte=start_dt).iterator(chunk_size=250):
            self.process_away_log(away_log, now_d);

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated.'))
        )
