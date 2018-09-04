# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from shared_foundation import constants
from shared_foundation.models import SharedFranchise
from shared_foundation.models import SharedUser
from shared_foundation.utils import get_jwt_token_and_orig_iat
from tenant_foundation.models import Customer


TEST_SCHEMA_NAME = "london"
TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestTenantCustomerViews(TenantTestCase):
    """
    Console:
    python manage.py test tenant_customer.tests
    """

    #------------------#
    # Setup Unit Tests #
    #------------------#

    def setup_tenant(tenant):
        """Tenant Schema"""
        tenant.schema_name = TEST_SCHEMA_NAME
        tenant.name='Over 55 (London) Inc.',
        tenant.alternate_name="Over55",
        tenant.description="Located at the Forks of the Thames in ...",
        tenant.address_country="CA",
        tenant.address_locality="London",
        tenant.address_region="Ontario",
        tenant.post_office_box_number="", # Post Offic #
        tenant.postal_code="N6H 1B4",
        tenant.street_address="78 Riverside Drive",
        tenant.street_address_extra="", # Extra line.

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
        super(TestTenantCustomerViews, self).setUp()

        # Setup our app and account.
        call_command('init_app', verbosity=0)
        call_command('populate_tenant_content', TEST_SCHEMA_NAME, verbosity=0)
        call_command('populate_tenant_sample_db', TEST_SCHEMA_NAME, verbosity=0)

        # Get user and credentials.
        user = SharedUser.objects.get(email="bart+executive@workery.ca")
        token, orig_iat = get_jwt_token_and_orig_iat(user)

        # Setup our clients.
        self.anon_c = TenantClient(self.tenant)
        self.auth_c = TenantClient(self.tenant, HTTP_AUTHORIZATION='JWT {0}'.format(token))
        self.auth_c.login(
            username = "bart+executive@workery.ca",
            password = "123P@$$w0rd"
        )

    def tearDown(self):
        """
        Run at the end of every unit test.
        """
        # Delete previous data.
        SharedUser.objects.all().delete()

        # Delete our clients.
        del self.anon_c
        del self.auth_c

        # Finish teardown.
        super(TestTenantCustomerViews, self).tearDown()

    def test_customer_summary_page(self):
        a_url = self.tenant.reverse(reverse_id='workery_tenant_customer_summary')
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pick_customer_create_page(self):
        a_url = self.tenant.reverse(reverse_id='workery_tenant_pick_customer_create')
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_residential_customer_create_page(self):
        a_url = self.tenant.reverse(reverse_id='workery_tenant_residential_customer_create')
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_residential_customer_confirm_create_page(self):
        a_url = self.tenant.reverse(reverse_id='workery_tenant_residential_customer_confirm_create')
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_commercial_customer_create_page(self):
        a_url = self.tenant.reverse(reverse_id='workery_tenant_commercial_customer_create')
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_commercial_customer_confirm_create_page(self):
        a_url = self.tenant.reverse(reverse_id='workery_tenant_commercial_customer_confirm_create')
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_list_page(self):
        a_url = self.tenant.reverse(reverse_id='workery_tenant_customer_list')
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_search_page(self):
        a_url = self.tenant.reverse(reverse_id='workery_tenant_customer_search')
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_search_results_page(self):
        a_url = self.tenant.reverse(reverse_id='workery_tenant_customer_search_results')+"?keyword=test"
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_lite_retrieve_page(self):
        customer = Customer.objects.all().first()
        a_url = self.tenant.reverse(
            reverse_id='workery_tenant_customer_lite_retrieve',
            reverse_args=[
                'summary',
                int(customer.id)
            ]
        )
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_full_retrieve_page(self):
        customer = Customer.objects.all().first()
        a_url = self.tenant.reverse(
            reverse_id='workery_tenant_customer_full_retrieve',
            reverse_args=[
                'summary',
                int(customer.id)
            ]
        )
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_retrieve_for_jobs_list_page(self):
        customer = Customer.objects.all().first()
        a_url = self.tenant.reverse(
            reverse_id='workery_tenant_customer_retrieve_for_jobs_list',
            reverse_args=[
                'summary',
                int(customer.id)
            ]
        )
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_retrieve_for_comment_list_and_create_page(self):
        customer = Customer.objects.all().first()
        a_url = self.tenant.reverse(
            reverse_id='workery_tenant_customer_retrieve_for_comment_list_and_create',
            reverse_args=[
                'summary',
                int(customer.id)
            ]
        )
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_residential_customer_update_page(self):
        customer = Customer.objects.all().first()
        a_url = self.tenant.reverse(
            reverse_id='workery_tenant_residential_customer_update',
            reverse_args=[
                'summary',
                int(customer.id)
            ]
        )
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_residential_blacklist_customer_update_page(self):
        customer = Customer.objects.all().first()
        a_url = self.tenant.reverse(
            reverse_id='workery_tenant_residential_blacklist_customer_update',
            reverse_args=[
                'summary',
                int(customer.id)
            ]
        )
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_commercial_customer_update_page(self):
        customer = Customer.objects.all().first()
        a_url = self.tenant.reverse(
            reverse_id='workery_tenant_commercial_customer_update',
            reverse_args=[
                'summary',
                int(customer.id)
            ]
        )
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_commercial_blacklist_customer_update_page(self):
        customer = Customer.objects.all().first()
        a_url = self.tenant.reverse(
            reverse_id='workery_tenant_commercial_blacklist_customer_update',
            reverse_args=[
                'summary',
                int(customer.id)
            ]
        )
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
