# -*- coding: utf-8 -*-
import json
from django.core.management import call_command
from django.db.models import Q
from django.db import transaction
from django.test import TestCase
from django.test import Client
from django.utils import translation
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django_rq import get_queue, get_worker
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from shared_foundation import constants
from shared_foundation.models import SharedUser
from shared_foundation.utils import get_jwt_token_and_orig_iat


TEST_SCHEMA_NAME = "mikasoftware"
TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class SharedFranchiseListAPIViewWithPublicSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.views.test_franchise_list_views
    """

    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(SharedFranchiseListAPIViewWithPublicSchemaTestCase, self).setUp()
        self.anon_client = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)

        # Update the tenant.
        self.tenant.name='Over 55 (London) Inc.',
        self.tenant.alternate_name="Over55",
        self.tenant.description="Located at the Forks of the Thames in ...",
        self.tenant.address_country="CA",
        self.tenant.address_locality="London",
        self.tenant.address_region="Ontario",
        self.tenant.post_office_box_number="", # Post Offic #
        self.tenant.postal_code="N6H 1B4",
        self.tenant.street_address="78 Riverside Drive",
        self.tenant.street_address_extra="", # Extra line.
        self.tenant.save()

        # Create our test user.
        call_command(
           'create_shared_account',
           TEST_USER_EMAIL,
           TEST_USER_PASSWORD,
           "Bart",
           "Mika",
           verbosity=0
        )

        # Initialize our test data.
        self.user = SharedUser.objects.get(email=TEST_USER_EMAIL)
        token, orig_iat = get_jwt_token_and_orig_iat(self.user)

        self.authorized_client = TenantClient(self.tenant, HTTP_AUTHORIZATION='JWT {0}'.format(token))
        self.authorized_client.login(
            username=TEST_USER_USERNAME,
            password=TEST_USER_PASSWORD
        )

    @transaction.atomic
    def tearDown(self):
        for user in SharedUser.objects.all():
            user.delete()
        del self.anon_client
        del self.authorized_client
        super(SharedFranchiseListAPIViewWithPublicSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_anonymous_get_with_200(self):
        url = reverse('workery_franchise_list_create_api_endpoint')
        response = self.anon_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("London", str(response.data))
        self.assertIn("Ontario", str(response.data))

    @transaction.atomic
    def test_anonymous_search_get_with_200_(self):
        url = reverse('workery_franchise_list_create_api_endpoint')+"?format=json&search=London"
        response = self.anon_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("London", str(response.data))
        self.assertIn("Ontario", str(response.data))

    @transaction.atomic
    def test_anonymous_post(self):
        url = reverse('workery_franchise_list_create_api_endpoint')
        post_data = json.dumps({
            "schema_name": "mikasoftware",
            "postal_code": "n6j4x4",
            "name": "Mika Software Corporation",
            "alternate_name": "Mika Software",
            "description": "An open source software company.",
            "url": "https://mikasoftware.com",
            "timezone_name": "America/Toronto",
            "address_country": "Canada",
            "address_locality": "London",
            "address_region": "Ontario",
            "postal_code": "N6J4X4",
            "street_address": "120 Centre Street",
            "street_address_extra": "Unit 102"
        })
        response = self.anon_client.post(url, data=post_data, content_type='application/json')
        get_worker().work(burst=True) # Processes all BACKGROUND jobs in FOREGROUND then stop. (Note: https://stackoverflow.com/a/12273705)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # self.assertIn("London", str(response.data))
        # self.assertIn("Ontario", str(response.data))

    @transaction.atomic
    def test_post_with_201(self):
        url = reverse('workery_franchise_list_create_api_endpoint')
        post_data = json.dumps({
            "schema_name": "mikasoftware",
            "postal_code": "n6j4x4",
            "name": "Mika Software Corporation",
            "alternate_name": "Mika Software",
            "description": "An open source software company.",
            "url": "https://mikasoftware.com",
            "timezone_name": "America/Toronto",
            "address_country": "Canada",
            "address_locality": "London",
            "address_region": "Ontario",
            "postal_code": "N6J4X4",
            "street_address": "120 Centre Street",
            "street_address_extra": "Unit 102"
        })
        response = self.authorized_client.post(url, data=post_data, content_type='application/json')
        get_worker().work(burst=True) # Processes all BACKGROUND jobs in FOREGROUND then stop. (Note: https://stackoverflow.com/a/12273705)
        print(response.content)
        print(response.data)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertIn("London", str(response.data))
        # self.assertIn("Ontario", str(response.data))
