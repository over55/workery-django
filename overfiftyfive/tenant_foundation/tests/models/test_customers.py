from django.core.management import call_command
from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from shared_foundation.models import O55User
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
        self.user = O55User.objects.create(
            first_name="Aurthor",
            last_name="Clarke",
            email=TEST_USER_EMAIL,
            username=get_unique_username_from_email(TEST_USER_EMAIL),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        self.customer = Customer.objects.create(
            user=self.user,
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

    def tearDown(self):
        Customer.objects.delete_all()
        del self.c
        self.user = None
        super(TestTenantCustomerModel, self).tearDown()

    def test_str(self):
        # CASE 1 OF 2:
        value = str(self.customer)
        self.assertIsNotNone(value)
        self.assertEqual("Aurthor C. Clarke", value)

        # CASE 2 OF 2:
        self.customer.middle_name = None
        value = str(self.customer)
        self.assertIsNotNone(value)
        self.assertEqual("Aurthor Clarke", value)
