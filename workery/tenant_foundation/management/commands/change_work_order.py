# -*- coding: utf-8 -*-
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
    VehicleType
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will change some work order for tenant specific data.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py change_work_order "london" "23530" "cancelled"
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('id', nargs='+', type=str)
        parser.add_argument('state', nargs='+', type=str)

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        worker_order_id = options['id'][0]
        state = options['state'][0]

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

        try:
            work_order = WorkOrder.objects.get(id=worker_order_id)
        except WorkOrder.DoesNotExist:
            raise CommandError(_('Work order does not exist!'))

        # Change state.
        work_order.state = state
        work_order.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully changed work order.'))
        )
