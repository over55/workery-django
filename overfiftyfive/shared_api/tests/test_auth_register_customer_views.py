# -*- coding: utf-8 -*-
import json
from django.core.management import call_command
from django.db.models import Q
from django.db import transaction
from django.test import TestCase
from django.test import Client
from django.utils import translation
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from shared_foundation import constants
from shared_foundation.models import SharedMe


TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class AuthRegisterCustomerViewsWithSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.test_auth_register_customer_views
    """
    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(AuthRegisterCustomerViewsWithSchemaTestCase, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)

    @transaction.atomic
    def tearDown(self):
        users = User.objects.all()
        for user in users.all():
            user.delete()
        del self.c
        super(AuthRegisterCustomerViewsWithSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_api_endpoint_with_success(self):
        url = reverse('o55_register_customer_api_endpoint')
        data = {
            'first_name': 'Bart',
            'last_name': 'Mika',
            'email': TEST_USER_EMAIL,
            'password': TEST_USER_PASSWORD,
            'password_repeat': TEST_USER_PASSWORD,
            'has_signed_tos': True,
            'schema_name': 'test',
            'telephone': '123 123-1234',
            'telephone_extension': '',
            'mobile': '',
            'address_country': 'Canada',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'post_office_box_number': '',
            'postal_code': 'N6H 1B4',
            'street_address': '78 Riverside Drive',
            'street_address_extra': ''
        }
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        # Confirm.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @transaction.atomic
    def test_api_endpoint_with_failure(self):
        url = reverse('o55_register_customer_api_endpoint')
        data = {
            'first_name': 'Bart',
            'last_name': 'Mika',
            'email': TEST_USER_EMAIL,
            'password': TEST_USER_PASSWORD,
            'password_repeat': TEST_USER_PASSWORD,
            'has_signed_tos': True,
            'schema_name': 'test',
            'telephone': '',
            'telephone_extension': '',
            'mobile': '',
            'address_country': 'Canada',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'post_office_box_number': '',
            'postal_code': 'N6H 1B4',
            'street_address': '78 Riverside Drive',
            'street_address_extra': ''
        }
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        # Confirm.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
