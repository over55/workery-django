# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from shared_foundation.models import SharedFranchise
from shared_foundation.models import SharedUser
from shared_foundation.models import SharedUser
from shared_foundation.utils import get_jwt_token_and_orig_iat


TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestSharedFranchiseViews(TenantTestCase):
    """
    Class used to test the web views.

    Console:
    python manage.py test shared_franchise.tests
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
        super(TestSharedFranchiseViews, self).setUp()

        # Setup our app and account.
        call_command('init_app', verbosity=0)
        call_command(
           'create_shared_account',
           TEST_USER_EMAIL,
           TEST_USER_PASSWORD,
           "Bart",
           "Mika",
           verbosity=0
        )

        # Get user and credentials.
        user = SharedUser.objects.get()
        token, orig_iat = get_jwt_token_and_orig_iat(user)

        # Setup our clients.
        self.anon_c = TenantClient(self.tenant)
        self.auth_c = TenantClient(self.tenant, HTTP_AUTHORIZATION='JWT {0}'.format(token))
        self.auth_c.login(
            username=TEST_USER_USERNAME,
            password=TEST_USER_PASSWORD
        )

        # Attach our user(s) to our test tenant organization.
        user.franchise = self.tenant
        user.save()

    def tearDown(self):
        """
        Run at the end of every unit test.
        """
        # Delete our clients.
        del self.anon_c
        del self.auth_c

        # Delete previous data.
        SharedUser.objects.all().delete()

        # Finish teardown.
        super(TestSharedFranchiseViews, self).tearDown()

    def test_shared_franchise_list_page(self):
        response = self.auth_c.get(reverse('workery_shared_franchise_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hared_franchise_create_1_of_3_page(self):
        response = self.auth_c.get(
            reverse('workery_shared_franchise_create_1_of_3'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_shared_franchise_create_2_of_3_page(self):
        response = self.auth_c.get(
            reverse('workery_shared_franchise_create_2_of_3'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_shared_franchise_create_3_of_3_page(self):
        response = self.auth_c.get(
            reverse('workery_shared_franchise_create_3_of_3'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
