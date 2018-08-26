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


class APIAuthResetPasswordViewslWithSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.views.test_auth_reset_password_views
    """

    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(APIAuthResetPasswordViewslWithSchemaTestCase, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)
        call_command(
           'create_shared_account',
           TEST_USER_EMAIL,
           TEST_USER_PASSWORD,
           "Bart",
           "Mika",
           verbosity=0
        )

    @transaction.atomic
    def tearDown(self):
        SharedUser.objects.delete_all()
        del self.c
        super(APIAuthResetPasswordViewslWithSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_api_endpoint_with_success(self):
        # Get credentials
        me = SharedUser.objects.get()
        pr_access_code = me.generate_pr_code()

        # Log out.
        url = reverse('workery_reset_password_api_endpoint')
        data = {
            'password': TEST_USER_PASSWORD,
            'password_repeat': TEST_USER_PASSWORD,
            'pr_access_code': pr_access_code
        }
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        # Confirm.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @transaction.atomic
    def test_api_endpoint_with_bad_pr_access_code(self):
        # Get credentials
        me = SharedUser.objects.get()
        pr_access_code = me.generate_pr_code()

        # Log out.
        url = reverse('workery_reset_password_api_endpoint')
        data = {
            'password': TEST_USER_PASSWORD,
            'password_repeat': TEST_USER_PASSWORD,
            'pr_access_code': "some-bad-pr-access-code"
        }
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        # Confirm.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def test_api_endpoint_with_bad_password(self):
        # Log out.
        url = reverse('workery_reset_password_api_endpoint')
        data = {
            'password': "some-bad-password",
            'password_repeat': "some-bad-password-plus-mismatching-entry",
            'pr_access_code': "some-bad-pr-access-code"
        }
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        # Confirm.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify password error messages.
        self.assertIn("Password", str(response.data))
        self.assertIn("uppercase", str(response.data))
