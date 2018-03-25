# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from shared_foundation.models import SharedUser
from shared_foundation.utils import *
from tenant_foundation.models import Customer


TEST_USER_EMAIL = "acclarke@verfiftyfive.com"


class TestTenantCustomerModel(TenantTestCase):
    """
    Console:
    python manage.py test tenant_foundation.tests.models.test_customers
    """

    def setUp(self):
        super(TestTenantCustomerModel, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)
        self.owner = SharedUser.objects.create(
            first_name="Aurthor",
            last_name="Clarke",
            email=TEST_USER_EMAIL,
            username=get_unique_username_from_email(TEST_USER_EMAIL),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )

    def tearDown(self):
        Customer.objects.delete_all()
        del self.c
        self.owner.delete()
        super(TestTenantCustomerModel, self).tearDown()

    def test_str(self):
        customer = Customer.objects.create(
            owner=self.owner,
            email=TEST_USER_EMAIL,
            given_name="Aurthor",
            last_name="Clarke",
            middle_name="C.",
            address_country="CA",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="", # Post Offic #
            postal_code="N6H 1B4",
            street_address="78 Riverside Drive",
            street_address_extra="", # Extra line.
        )

        # CASE 1 OF 2:
        value = str(customer)
        self.assertIsNotNone(value)
        self.assertEqual("Aurthor C. Clarke", value)

        # CASE 2 OF 2:
        customer.middle_name = None
        value = str(customer)
        self.assertIsNotNone(value)
        self.assertEqual("Aurthor Clarke", value)
    #
    def test_save_validation(self):
        # CASE 1 OF 3: Attempt to save the model when the `User` objects
        #              email is different then the `Customer` objects email
        #              field.
        try:
            Customer.objects.create(
                owner=self.owner,
                email='test@test.com',
                given_name="Aurthor",
                last_name="Clarke",
                middle_name="C.",
                address_country="CA",
                address_locality="London",
                address_region="Ontario",
                post_office_box_number="", # Post Offic #
                postal_code="N6H 1B4",
                street_address="78 Riverside Drive",
                street_address_extra="", # Extra line.
            )
        except Exception as e:
            self.assertIsNotNone(e)

        # CASE 2 OF 3: Attempt to save the model when we have no `User` object
        #              customerd BUT we have an email field set. This should
        #              find the email and error.
        try:
            Customer.objects.create(
                owner=None,
                email=TEST_USER_EMAIL,
                given_name="Aurthor",
                last_name="Clarke",
                middle_name="C.",
                address_country="CA",
                address_locality="London",
                address_region="Ontario",
                post_office_box_number="", # Post Offic #
                postal_code="N6H 1B4",
                street_address="78 Riverside Drive",
                street_address_extra="", # Extra line.
            )
        except Exception as e:
            self.assertIsNotNone(e)

        # CASE 3 OF 3: Run a successful save.
        customer = Customer.objects.create(
            owner=None,
            email='test@test.com',
            given_name="Aurthor",
            last_name="Clarke",
            middle_name="C.",
            address_country="CA",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="", # Post Offic #
            postal_code="N6H 1B4",
            street_address="78 Riverside Drive",
            street_address_extra="", # Extra line.
        )

        # Attempt to add wrong matching emails.
        try:
            customer.owner = self.owner
            customer.save()
        except Exception as e:
            self.assertIsNotNone(e)

        # Attempt to add correct matching emails.
        customer.owner = self.owner
        customer.email = TEST_USER_EMAIL
        customer.save()

    def test_full_text_search(self):
        # Setup the test.
        customer = Customer.objects.create(
            owner=self.owner,
            email=TEST_USER_EMAIL,
            given_name="Aurthor",
            last_name="Clarke",
            middle_name="C.",
            address_country="CA",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="", # Post Offic #
            postal_code="N6H 1B4",
            street_address="78 Riverside Drive",
            street_address_extra="", # Extra line.
        )

        # Test and verify.
        querysets = Customer.objects.full_text_search('Aurthor')
        self.assertEqual(querysets.count(), 1)

    def test_partial_text_search(self):
        # Setup the test.
        customer = Customer.objects.create(
            owner=self.owner,
            email=TEST_USER_EMAIL,
            given_name="Aurthor",
            last_name="Clarke",
            middle_name="C.",
            address_country="CA",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="", # Post Offic #
            postal_code="N6H 1B4",
            street_address="78 Riverside Drive",
            street_address_extra="", # Extra line.
        )

        # Test and verify.
        querysets = Customer.objects.partial_text_search('Aurthor')
        self.assertEqual(querysets.count(), 1)
