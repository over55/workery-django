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
from tenant_foundation.models import Partner


TEST_SCHEMA_NAME = "london"
TEST_USER_EMAIL = "bart+executive@workery.ca"
TEST_USER_USERNAME = "bart+executive@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"


class TestTenantPartnerViews(TenantTestCase):
    """
    Console:
    python manage.py test tenant_partner.tests
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
        super(TestTenantPartnerViews, self).setUp()

        # Setup our app and account.
        call_command('init_app', verbosity=0)
        call_command('populate_tenant_content', TEST_SCHEMA_NAME, verbosity=0)
        call_command('populate_tenant_sample_db', TEST_SCHEMA_NAME, verbosity=0)

            # Get user and credentials.
        user = SharedUser.objects.get(email='bart+executive@workery.ca')
        token, orig_iat = get_jwt_token_and_orig_iat(user)

        # Setup our clients.
        self.anon_c = TenantClient(self.tenant)
        self.auth_c = TenantClient(self.tenant, HTTP_AUTHORIZATION='JWT {0}'.format(token))
        self.auth_c.login(
            username=TEST_USER_USERNAME,
            password=TEST_USER_PASSWORD
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
        super(TestTenantPartnerViews, self).tearDown()

    def test_summary_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_partner_summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Partner', str(response.content))

    def test_create_confirmation_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_partner_confirm_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Add Partner', str(response.content))

    def test_create_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_partner_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Add Partner', str(response.content))

    def test_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_partner_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Partner List', str(response.content))

    def test_search_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_partner_search'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Partners Search', str(response.content))

    def test_search_confirmation_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_partner_search_results')+'?keyword='+TEST_USER_EMAIL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Partner Search', str(response.content))
        self.assertIn(TEST_USER_EMAIL, str(response.content))

    def test_lite_retrieve_page(self):
        partner = Partner.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_partner_lite_retrieve', reverse_args=['summary', int(partner.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Partner', str(response.content))
        # self.assertIn('Gendo', str(response.content))

    def test_full_retrieve_page(self):
        partner = Partner.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_partner_full_retrieve', reverse_args=['summary', int(partner.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Partner', str(response.content))
        # self.assertIn('Gendo', str(response.content))

    def test_comments_retrieve_page(self):
        partner = Partner.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_partner_retrieve_for_comment_list', reverse_args=['summary', int(partner.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Partner', str(response.content))
        self.assertIn('Add Comment/Note', str(response.content))

    def test_update_page(self):
        partner = Partner.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_partner_update', reverse_args=['summary', int(partner.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Partner', str(response.content))
        self.assertIn('Edit Partner', str(response.content))
