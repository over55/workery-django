# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email,
    int_or_none
)
from rest_framework.authtoken.models import Token
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
    Order,
    # OrderComment,
    Staff,
    Tag
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py delete_tenant_account "london" "bart+manager@workery.ca"
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('email', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        email = options['email'][0]

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(schema_name, True) # Switch to Tenant.

        # Defensive Code: Prevent continuing if the email already exists.
        if not SharedUser.objects.filter(email=email).exists():
            raise CommandError(_('Email does not exists, please pick another email.'))

        # Create the user.
        user = SharedUser.objects.get(email=email)
        user.delete()
        self.stdout.write(self.style.SUCCESS(_('Deleted "User" object.')))

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully deleted a tenant account.'))
        )
