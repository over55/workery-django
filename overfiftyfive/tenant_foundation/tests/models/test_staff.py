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
from tenant_foundation.models import Staff


TEST_USER_EMAIL = "acclarke@verfiftyfive.com"


class TestTenantStaffModel(TenantTestCase):
    """
    Console:
    python manage.py test tenant_foundation.tests.models.test_staff
    """

    def setUp(self):
        super(TestTenantStaffModel, self).setUp()
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
        self.staff = Staff.objects.create(
            user=self.user,
            given_name="Aurthor",
            last_name="Clarke",
            middle_name="C."
        )

    def tearDown(self):
        Staff.objects.delete_all()
        del self.c
        self.staff = None
        self.user.delete()
        super(TestTenantStaffModel, self).tearDown()

    def test_str(self):
        # CASE 1 OF 2:
        value = str(self.staff)
        self.assertIsNotNone(value)
        self.assertEqual("Aurthor C. Clarke", value)

        # CASE 2 OF 2:
        self.staff.middle_name = None
        value = str(self.staff)
        self.assertIsNotNone(value)
        self.assertEqual("Aurthor Clarke", value)

    def test_get_by_email_or_none(self):
        # CASE 1 OF 2:
        staff = Staff.objects.get_by_email_or_none(TEST_USER_EMAIL)
        self.assertIsNotNone(staff)

        # CASE 2 OF 2:
        staff = Staff.objects.get_by_email_or_none("trudy@overfiftyfive.com")
        self.assertIsNone(staff)

    def test_get_by_user_or_none(self):
        # CASE 1 OF 2:
        staff = Staff.objects.get_by_user_or_none(self.user)
        self.assertIsNotNone(staff)

        # CASE 2 OF 2:
        staff = Staff.objects.get_by_user_or_none(None)
        self.assertIsNone(staff)
