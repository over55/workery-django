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
    help = _('Command will run `hotfix_17`.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_17 "london"
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

        # ITERATE THROUGH ALL THE CUSTOMERS AND IF A NULL JOIN DATE IS FOUND
        # THEN WE ASSIGN IT THE CREATION DATETIME.
        for customer in Customer.objects.iterator(chunk_size=250):
            if customer.join_date is None:
                customer.join_date = customer.created
                customer.save()

                # For debugging purposes.
                self.stdout.write(
                    self.style.SUCCESS(_('Updated customer # %(id)s.') %{
                        'id': str(customer.id)
                    })
                )

        # ITERATE THROUGH ALL THE ASSOCIATES AND IF A NULL JOIN DATE IS FOUND
        # THEN WE ASSIGN IT THE CREATION DATETIME.
        for associate in Associate.objects.iterator(chunk_size=250):
            if associate.join_date is None:
                associate.join_date = customer.created
                associate.save()

                # For debugging purposes.
                self.stdout.write(
                    self.style.SUCCESS(_('Updated associate # %(id)s.') %{
                        'id': str(customer.id)
                    })
                )

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated.'))
        )
