# -*- coding: utf-8 -*-
from django.core.management import call_command
from starterkit.utils import get_unique_username_from_email
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.models import *


TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestFranchise(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.models.test_franchise
    """

    def setUp(self):
        super(TestFranchise, self).setUp()
        self.c = TenantClient(self.tenant)
        self.user = O55User.objects.create(
            first_name="Bart",
            last_name="Mika",
            email=TEST_USER_EMAIL,
            username=get_unique_username_from_email(TEST_USER_EMAIL),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        self.tenant.name = "Over55 (London) Inc."
        self.tenant.frontline_staff.add(self.user)

    def tearDown(self):
        del self.c
        super(TestFranchise, self).tearDown()

    def test_str(self):
        self.assertIsNotNone(str(self.tenant))
        self.assertIn("Over55 (London) Inc.", str(self.tenant))

    def test_get_by_email_or_none(self):
        # CASE 1 OF 2:
        franchise = SharedFranchise.objects.get_by_email_or_none(TEST_USER_EMAIL)
        self.assertIsNotNone(franchise)

        # CASE 2 OF 2:
        franchise = SharedFranchise.objects.get_by_email_or_none("trudy@overfiftyfive.com")
        self.assertIsNone(franchise)

    def test_reverse(self):
        # Attempt to lookup a URL.
        url = self.tenant.reverse('o55_tenant_dashboard_master')

        # Verify the URL.
        self.assertIsNotNone(url)
        self.assertIn("http://test.overfiftyfive.com/en/dashboard", url)
