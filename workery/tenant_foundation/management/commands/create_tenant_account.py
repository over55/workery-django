# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
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
    WorkOrder,
    # WorkOrderComment,
    Staff,
    Tag
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_tenant_account "london" 2 "bart+manager@workery.ca" "123password" "Bart" "Mika" "123 123-1234" "" "123 123-1234" "CA" "London" "Ontario" "" "N6H 1B4" "78 Riverside Drive" ""
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('group_id', nargs='+', type=int)
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)
        parser.add_argument('first_name', nargs='+', type=str)
        parser.add_argument('last_name', nargs='+', type=str)
        parser.add_argument('telephone', nargs='+', type=str)
        parser.add_argument('telephone_extension', nargs='+', type=str)
        parser.add_argument('other_telephone', nargs='+', type=str)
        parser.add_argument('address_country', nargs='+', type=str)
        parser.add_argument('address_locality', nargs='+', type=str)
        parser.add_argument('address_region', nargs='+', type=str)
        parser.add_argument('post_office_box_number', nargs='+', type=str)
        parser.add_argument('postal_code', nargs='+', type=str)
        parser.add_argument('street_address', nargs='+', type=str)
        parser.add_argument('street_address_extra', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        group_id = int(options['group_id'][0])
        email = options['email'][0]
        password = options['password'][0]
        first_name = options['first_name'][0]
        last_name = options['last_name'][0]
        telephone = options['telephone'][0]
        telephone_extension = options['telephone_extension'][0]
        other_telephone = options['other_telephone'][0]
        address_country = options['address_country'][0]
        address_locality = options['address_locality'][0]
        address_region = options['address_region'][0]
        post_office_box_number = options['post_office_box_number'][0]
        postal_code = options['postal_code'][0]
        street_address = options['street_address'][0]
        street_address_extra = options['street_address_extra'][0]

        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        # Defensive Code: Prevent continuing if the email already exists.
        if SharedUser.objects.filter(email=email).exists():
            raise CommandError(_('Email already exists, please pick another email.'))

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        # Create the user.
        user = SharedUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=True,
            franchise=franchise,
            was_email_activated=True

        )
        self.stdout.write(self.style.SUCCESS(_('Created a "SharedUser" object.')))

        # Generate and assign the password.
        user.set_password(password)
        user.save()

        # Generate the private access key.
        token = Token.objects.create(user=user)

        self.stdout.write(self.style.SUCCESS(_('Created a "Token" object.')))

        # Attach our user to the group.
        user.groups.add(group_id)

        # Connection will set it back to our tenant.
        connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

        # Create `Manager` or `Frontline Staff`.
        if group_id == constants.MANAGEMENT_GROUP_ID or group_id == constants.FRONTLINE_GROUP_ID:
            Staff.objects.create(
                owner=user,
                given_name=first_name,
                last_name=last_name,
                email=email,
                telephone=telephone,
                telephone_extension=telephone_extension,
                other_telephone=other_telephone,
                address_country=address_country,
                address_locality=address_locality,
                address_region=address_region,
                post_office_box_number=post_office_box_number,
                postal_code=postal_code,
                street_address=street_address,
                street_address_extra=street_address_extra,
            )
            self.stdout.write(self.style.SUCCESS(_('Created a "Staff" object.')))

        # Create `Associate`.
        if group_id == constants.ASSOCIATE_GROUP_ID:
            Associate.objects.create(
                owner=user,
                given_name=first_name,
                last_name=last_name,
                email=email,
                telephone=telephone,
                telephone_extension=telephone_extension,
                other_telephone=other_telephone,
                address_country=address_country,
                address_locality=address_locality,
                address_region=address_region,
                post_office_box_number=post_office_box_number,
                postal_code=postal_code,
                street_address=street_address,
                street_address_extra=street_address_extra,
            )
            self.stdout.write(self.style.SUCCESS(_('Created an "Associate" object.')))

        # Create `Customer`.
        if group_id == constants.CUSTOMER_GROUP_ID:
            Customer.objects.create(
                owner=user,
                given_name=first_name,
                last_name=last_name,
                email=email,
                telephone=telephone,
                telephone_extension=telephone_extension,
                other_telephone=other_telephone,
                address_country=address_country,
                address_locality=address_locality,
                address_region=address_region,
                post_office_box_number=post_office_box_number,
                postal_code=postal_code,
                street_address=street_address,
                street_address_extra=street_address_extra,
            )
            self.stdout.write(self.style.SUCCESS(_('Created a "Customer" object.')))

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully created a tenant account.'))
        )
