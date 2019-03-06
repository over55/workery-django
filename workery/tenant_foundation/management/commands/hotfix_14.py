# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from shared_foundation.constants import *
from shared_foundation.models import (
    SharedUser,
    SharedFranchise
)
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Associate,
    # Comment,
    Customer,
    InsuranceRequirement,
    Organization,
    WORK_ORDER_STATE,
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
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder,
    WorkOrder,
    TaskItem
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will run `hotfix_14`.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_14 "london"
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

        for order in WorkOrder.objects.iterator(chunk_size=250):

            # STEP 1: UPDATE THE "INVOICE_IDS".
            if order.invoice_id:
                order.invoice_ids = str(order.invoice_id)
            else:
                order.invoice_ids = ""
            order.save()

            # For debugging purposes.
            self.stdout.write(
                self.style.SUCCESS(_('Updated %(id)s.') %{
                    'id': str(order.id)
                })
            )

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated.'))
        )
