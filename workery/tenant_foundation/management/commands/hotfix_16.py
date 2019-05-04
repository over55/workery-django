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
    TaskItem,
    HowHearAboutUsItem
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will run `hotfix_16` which migrates fields.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_16 "london"
        """
        parser.add_argument('schema_name', nargs='+', type=str)

    def process_customer(self, customer):
        # Map our new change.
        if customer.how_hear == 1:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=1)

        if customer.how_hear == 2:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=9)

        if customer.how_hear == 3:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=5)

        if customer.how_hear == 5:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=10)

        if customer.how_hear == 6:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=11)

        if customer.how_hear == 7:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=12)

        if customer.how_hear == 8:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=13)

        if customer.how_hear == 11:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=14)

        if customer.how_hear == 12:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=15)

        if customer.how_hear == 13:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=16)

        if customer.how_hear == 14:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=17)

        if customer.how_hear == 15:
            customer.how_hear_about_us = HowHearAboutUsItem.objects.get(id=18)

        # Save our change.
        customer.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Updated customer %(id)s.') %{
                'id': str(customer.id)
            })
        )

    def process_associate(self, associate):
        # Map our new change.
        if associate.how_hear == 1:
            associate.how_hear_about_us = HowHearAboutUsItem.objects.get(id=1)

        if associate.how_hear == 2:
            associate.how_hear_about_us = HowHearAboutUsItem.objects.get(id=2)

        if associate.how_hear == 3:
            associate.how_hear_about_us = HowHearAboutUsItem.objects.get(id=3)

        if associate.how_hear == 4:
            associate.how_hear_about_us = HowHearAboutUsItem.objects.get(id=4)

        if associate.how_hear == 5:
            associate.how_hear_about_us = HowHearAboutUsItem.objects.get(id=5)

        if associate.how_hear == 6:
            associate.how_hear_about_us = HowHearAboutUsItem.objects.get(id=6)

        if associate.how_hear == 7:
            associate.how_hear_about_us = HowHearAboutUsItem.objects.get(id=7)

        if associate.how_hear == 8:
            associate.how_hear_about_us = HowHearAboutUsItem.objects.get(id=8)

        # Save our change.
        associate.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Updated associate %(id)s.') %{
                'id': str(associate.id)
            })
        )


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

        # Process the customers.
        for customer in Customer.objects.iterator(chunk_size=250):
            try:
                self.process_customer(customer)
            except Exception as e:
                print("ERROR CUSTOMER", customer.id, "-", e)

        # Process the associates.
        for associate in Associate.objects.iterator(chunk_size=250):
            try:
                self.process_associate(associate)
            except Exception as e:
                print("ERROR ASSOCIATE", associate.id, "-", e)

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated.'))
        )
