# -*- coding: utf-8 -*-
import sys
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from rest_framework.authtoken.models import Token
from shared_foundation import constants
from shared_foundation.models import (
    SharedUser,
    SharedFranchise
)
from tenant_foundation.models import (
    Associate,
    Comment,
    Customer,
    Organization,
    Order,
    OrderComment,
    Staff,
    Tag
)
from tenant_foundation.utils import *


TEST_SAMPLE_USER_PASSWORD = "123P@$$w0rd"


class Command(BaseCommand):
    """
    Run manually in console:
    python manage.py populate_tenant_sample_db "london"
    """
    help = _('Command will create a sample d')

    def add_arguments(self, parser):
        parser.add_argument('schema_name', nargs='?', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name']

        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        if len(sys.argv) > 1 and sys.argv[1] == 'test':
            self.begin_importing_for_franchise(franchise)

    def create_user(self, franchise, first_name, last_name, email, is_active, is_superuser, is_staff, password, was_email_activated, group_id):
        # Create the user.
        user = SharedUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=is_active,
            franchise=franchise,
            was_email_activated=was_email_activated
        )

        # Generate and assign the password.
        user.set_password(password)
        user.save()

        # Generate the private access key.
        token = Token.objects.create(user=user)

        # Attach our user to the group.
        user.groups.add(group_id)

        return user

    def begin_importing_for_franchise(self, franchise):
        user1 = self.create_user(
            franchise=franchise,
            first_name="Bart",
            last_name="Mika",
            email="bart+executive@workery.ca",
            is_active=True,
            is_superuser=True,
            is_staff=True,
            password=TEST_SAMPLE_USER_PASSWORD,
            was_email_activated=True,
            group_id=constants.EXECUTIVE_GROUP_ID
        )
        user2 = self.create_user(
            franchise=franchise,
            first_name="Bartlomiej",
            last_name="Mika",
            email="bart+manager@workery.ca",
            is_active=True,
            is_superuser=True,
            is_staff=True,
            password=TEST_SAMPLE_USER_PASSWORD,
            was_email_activated=True,
            group_id=constants.MANAGEMENT_GROUP_ID
        )
        user3 = self.create_user(
            franchise=franchise,
            first_name="Frank",
            last_name="Herbert",
            email="fherbert@workery.ca",
            is_active=True,
            is_superuser=True,
            is_staff=True,
            password=TEST_SAMPLE_USER_PASSWORD,
            was_email_activated=True,
            group_id=constants.FRONTLINE_GROUP_ID
        )
        user4 = self.create_user(
            franchise=franchise,
            first_name="Rei",
            last_name="Ayanami",
            email="rayanami@workery.ca",
            is_active=True,
            is_superuser=True,
            is_staff=True,
            password=TEST_SAMPLE_USER_PASSWORD,
            was_email_activated=True,
            group_id=constants.ASSOCIATE_GROUP_ID
        )
        user5 = self.create_user(
            franchise=franchise,
            first_name="Shinji",
            last_name="Ikari",
            email="sikari@workery.ca",
            is_active=True,
            is_superuser=True,
            is_staff=True,
            password=TEST_SAMPLE_USER_PASSWORD,
            was_email_activated=True,
            group_id=constants.CUSTOMER_GROUP_ID
        )

        # Connection will set it back to our tenant.
        connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

        # # Create `Manager` or `Frontline Staff`.
        Staff.objects.create(
            owner=user1,
            telephone="1234567890",
            telephone_extension="",
            other_telephone="1234567890",
            address_country="Canada",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="",
            postal_code="A1A1A1",
            street_address="100 Big Walk Way Street",
            street_address_extra="",
        )
        Staff.objects.create(
            owner=user2,
            telephone="1112223333",
            telephone_extension="",
            other_telephone="1112223333",
            address_country="Canada",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="",
            postal_code="B1B1B1",
            street_address="1 Long Peace Street Street",
            street_address_extra="",
        )
        Staff.objects.create(
            owner=user3,
            telephone="1002003000",
            telephone_extension="",
            other_telephone="1002003000",
            address_country="Canada",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="",
            postal_code="C1C1C1",
            street_address="160 Grey Street",
            street_address_extra="",
        )

        Associate.objects.create(
            owner=user4,
            telephone="1102203300",
            telephone_extension="",
            other_telephone="1102203300",
            address_country="Canada",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="",
            postal_code="D1D1D1",
            street_address="120 Hill Street",
            street_address_extra="",
        )

        Customer.objects.create(
            owner=user5,
            telephone="1112223330",
            telephone_extension="",
            other_telephone="1112223330",
            address_country="Canada",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="",
            postal_code="E1E1E1",
            street_address="101 Cheep Street",
            street_address_extra="",
        )
