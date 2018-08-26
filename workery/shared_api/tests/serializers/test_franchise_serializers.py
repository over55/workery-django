# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.db.models import Q
from django.db import transaction
from django.test import TestCase
from django.test import Client
from django.utils import translation
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django_rq import get_queue, get_worker
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError

from shared_foundation import constants
from shared_foundation.models import SharedUser, SharedFranchise
from shared_api.serializers.franchise_serializers import SharedFranchiseListCreateSerializer


TEST_SCHEMA_NAME = "test"
TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class SharedFranchiseListCreateSerializerWithPublicSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.serializers.test_franchise_serializers
    """

    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(SharedFranchiseListCreateSerializerWithPublicSchemaTestCase, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)

        # BUGFIX: In case a user was not deleted previously.
        SharedUser.objects.delete_all()

    @transaction.atomic
    def tearDown(self):
        del self.c
        SharedUser.objects.delete_all()
        super(SharedFranchiseListCreateSerializerWithPublicSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_validate_with_success(self):
        post_data = {
            'schema_name': 'mikasoftware',
            'postal_code': 'n6j4x4',
            'name': 'Mika Software Corporation',
            'alternate_name': 'Mika Software',
            'description': 'An open source software company.',
            'url': 'https://mikasoftware.com',
            'timezone_name': 'America/Toronto',
            'address_country': 'Canada',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'postal_code': 'N6J4X4',
            'street_address': '120 Centre Street',
            'street_address_extra': 'Unit 102'
        }
        serializer = SharedFranchiseListCreateSerializer(data=post_data)
        result = serializer.is_valid(raise_exception=True)
        serializer.save() # Run the code which will create a new job in BACKGROUND thread.
        get_worker().work(burst=True) # Processes all BACKGROUND jobs in FOREGROUND then stop. (Note: https://stackoverflow.com/a/12273705)
        self.assertTrue(result)
        franchise = SharedFranchise.objects.get(schema_name='mikasoftware')
        self.assertIsNotNone(franchise)
