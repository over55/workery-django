# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django_tenants.utils import tenant_context

from shared_foundation import constants
from shared_foundation.models import (
    SharedUser,
    SharedFranchise,
    SharedUser
)
from tenant_foundation.models import (
    Associate,
    # Comment,
    Customer,
    Organization,
    WorkOrder,
    # WorkOrderComment,
    Staff,
    Tag
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will fetch all details about a user.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py retrieve_account_by_email "bart+manager@workery.ca"
        """
        parser.add_argument('email', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        email = options['email'][0]

        # Defensive Code: Prevent continuing if the email already exists.
        if not SharedUser.objects.filter(email=email).exists():
            raise CommandError(_('Email does not exists, please pick another email.'))

        # Create the user.
        user = SharedUser.objects.get(email=email)
        self.stdout.write(self.style.SUCCESS(_('Retrieved "User" object.')))
        self.stdout.write(self.style.SUCCESS("-------------------------------"))
        self.stdout.write(self.style.SUCCESS("Name: %s" % user.get_full_name() ))
        self.stdout.write(self.style.SUCCESS("ID: %s" % user.id ))
        self.stdout.write(self.style.SUCCESS("-------------------------------"))

        for franchise in SharedFranchise.objects.filter(~Q(schema_name="public")).iterator():
            with tenant_context(franchise):
                associate = Associate.objects.filter(
                    Q(owner=user)|
                    Q(email=email)
                ).first()
                staff = Staff.objects.filter(
                    Q(owner=user)|
                    Q(email=email)
                ).first()
                customer = Customer.objects.filter(
                    Q(owner=user)|
                    Q(email=email)
                ).first()
                if associate or staff or customer:
                    self.stdout.write(self.style.SUCCESS("Found in Tenant: %s" % franchise.schema_name ))
                    if associate:
                        self.stdout.write(self.style.SUCCESS("\tAssociate ID: %s" % associate.id ))
                    if staff:
                        self.stdout.write(self.style.SUCCESS("\tStaff ID: %s" % staff.id ))
                    if customer:
                        self.stdout.write(self.style.SUCCESS("\tCustomer ID: %s" % customer.id ))
        self.stdout.write(self.style.SUCCESS("-------------------------------"))


        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully retrieved account.'))
        )
