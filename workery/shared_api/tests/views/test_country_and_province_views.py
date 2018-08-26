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
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from shared_foundation import constants
from shared_foundation.models import SharedUser


TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class APICountryAndProvinceViewslWithSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.views.test_country_and_province_views
    """

    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(APICountryAndProvinceViewslWithSchemaTestCase, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)

    @transaction.atomic
    def tearDown(self):
        SharedUser.objects.delete_all()
        del self.c
        super(APICountryAndProvinceViewslWithSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_country_api_endpoint_with_success(self):
        # Log out.
        url = reverse('workery_get_countries_api_endpoint')
        data = {}
        response = self.c.get(url, data, content_type='application/json')

        # Confirm.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @transaction.atomic
    def test_province_api_endpoint_with_success(self):
        # Log out.
        url = reverse('workery_get_provinces_api_endpoint')
        data = {}
        response = self.c.get(url, data, content_type='application/json')

        # Confirm.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
