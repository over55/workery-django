# -*- coding: utf-8 -*-
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
    WorkOrderDeposit,
    ResourceCategory,
    ResourceItem,
    ResourceItemSortOrder,
    Partner,
    SkillSet,
    Staff,
    Tag,
    VehicleType,
    WORK_ORDER_STATE
)
from tenant_foundation.constants import *
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('This hotfix should be run for issue `https://github.com/over55/workery-front/issues/218`.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_29 "london"
        """
        parser.add_argument('schema_name', nargs='+', type=str)

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

        self.stdout.write(
            self.style.SUCCESS(_('Starting updating associates...'))
        )

        # Find the default service fee.
        service_fee = WorkOrderServiceFee.objects.get(id=3)

        for associate in Associate.objects.all().iterator(chunk_size=250):
            try:
                with freeze_time(associate.last_modified):
                    associate.service_fee = service_fee
                    associate.save()
                    self.stdout.write(
                        self.style.SUCCESS(_('Updated associate %s.') % str(associate.id))
                    )
            except Exception as e:
                print(e)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated all unassigned associates.'))
        )
