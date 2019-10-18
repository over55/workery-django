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
    help = _('This hotfix should be run after applying `0067_auto_20191018_1808` migration.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_27 "london"
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
            self.style.SUCCESS(_('Starting updating orders...'))
        )
        for order in WorkOrder.objects.filter(state=WORK_ORDER_STATE.COMPLETED_AND_PAID).iterator(chunk_size=250):
            try:
                with freeze_time(order.last_modified):
                    # print(order.invoice_labour_amount)
                    # print(order.invoice_material_amount)
                    # print(order.invoice_waste_removal_amount)
                    order.invoice_sub_total_amount = order.invoice_labour_amount + order.invoice_material_amount + order.invoice_waste_removal_amount;
                    # print(order.invoice_sub_total_amount,"\n")
                    order.save()
                    self.stdout.write(
                        self.style.SUCCESS(_('Updated order %s.') % str(order.id))
                    )
            except Exception as e:
                print(e)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated all unassigned associates.'))
        )
