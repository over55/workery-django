# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework import status
from shared_foundation.models import SharedFranchise
from shared_foundation.models import SharedMe
from shared_foundation.models import O55User


TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestTenantDashboardViews(TenantTestCase):
    """
    Console:
    python manage.py test tenant_dashboard.tests.test_web_views
    """

    @classmethod
    def setUpClass(cls):
        """
        Run at the beginning before all the unit tests run.
        """
        super().setUpClass()

    def setUp(self):
        """
        Run at the beginning of every unit test.
        """
        super(TestTenantDashboardViews, self).setUp()

        # Setup our app and account.
        call_command('init_app', verbosity=0)
        call_command(
           'create_executive_account',
           TEST_USER_EMAIL,
           TEST_USER_PASSWORD,
           "Bart",
           "Mika",
           TEST_USER_TEL_NUM,
           TEST_USER_TEL_EX_NUM,
           TEST_USER_CELL_NUM,
           "CA",
           "London",
           "Ontario",
           "", # Post Offic #
           "N6H 1B4",
           "78 Riverside Drive",
           "", # Extra line.
           verbosity=0
        )

        # Get user and credentials.
        user = O55User.objects.get()
        token = Token.objects.get(user_id=user.id)

        # Setup our clients.
        self.anon_c = TenantClient(self.tenant)
        self.auth_c = TenantClient(self.tenant, HTTP_AUTHORIZATION='Token ' + token.key)
        self.auth_c.login(
            username=TEST_USER_USERNAME,
            password=TEST_USER_PASSWORD
        )

        # Attach our user(s) to our test tenant organization.
        self.tenant.managers.add(user)

    def tearDown(self):
        """
        Run at the end of every unit test.
        """
        # Delete our clients.
        del self.anon_c
        del self.auth_c

        # Delete previous data.
        O55User.objects.all().delete()

        # Finish teardown.
        super(TestTenantDashboardViews, self).tearDown()

    def test_master_page(self):
        response = self.auth_c.get(self.tenant.reverse('o55_tenant_dashboard_master'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Dashboard', str(response.content))
