# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
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
    OngoingWorkOrder
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will run `hotfix_2`.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_2 "london"
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

        work_orders = WorkOrder.objects.filter(
            Q(
                Q(state=WORK_ORDER_STATE.IN_PROGRESS) |
                Q(state=WORK_ORDER_STATE.ONGOING) |
                Q(state=WORK_ORDER_STATE.NEW)
            ) &
            Q(is_ongoing=True) &
            Q(ongoing_work_order__isnull=True)
        )
        for work_order in work_orders:
            print(work_order.id)
            work_order.ongoing_work_order = OngoingWorkOrder.objects.create(
                customer=work_order.customer,
                associate=work_order.associate,
                state=ONGOING_WORK_ORDER_STATE.RUNNING
            )
            work_order.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated.'))
        )
