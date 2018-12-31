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
    OngoingWorkOrder
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will run `hotfix_3`.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_3 "london"
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

        work_orders = WorkOrder.objects.all().prefetch_related(
            'customer',
            'associate'
        )
        for work_order in work_orders:
            # If customer is commercial, make sure job is commercial.
            if work_order.type_of == COMMERCIAL_JOB_TYPE_OF_ID:
                if work_order.customer.type_of == RESIDENTIAL_CUSTOMER_TYPE_OF_ID:
                    print("Commercial --> Residential", work_order)
                    work_order.type_of = RESIDENTIAL_JOB_TYPE_OF_ID
                    work_order.save()

            # If customer is residential, make sure job is residential.
            if work_order.type_of == RESIDENTIAL_JOB_TYPE_OF_ID:
                if work_order.customer.type_of == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
                    print("Residential --> Commercial", work_order)
                    work_order.type_of = COMMERCIAL_JOB_TYPE_OF_ID
                    work_order.save()

            # If status is set to unassigned but user is assigned.
            if work_order.type_of == UNASSIGNED_JOB_TYPE_OF_ID:
                if work_order.associate:
                    if work_order.customer.type_of == RESIDENTIAL_CUSTOMER_TYPE_OF_ID:
                        print("Unassigned --> Residential", work_order)
                        work_order.type_of = RESIDENTIAL_CUSTOMER_TYPE_OF_ID
                        work_order.save()
                    if work_order.customer.type_of == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
                        print("Unassigned --> Commercial", work_order)
                        work_order.type_of = COMMERCIAL_JOB_TYPE_OF_ID
                        work_order.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated.'))
        )
