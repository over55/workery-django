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


TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class APISendResetPasswordEmailWithSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.test_send_reset_password_email_views
    """
    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(APISendResetPasswordEmailWithSchemaTestCase, self).setUp()
        self.c = TenantClient(self.tenant)
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

    @transaction.atomic
    def tearDown(self):
        users = User.objects.all()
        for user in users.all():
            user.delete()
        del self.c
        super(APISendResetPasswordEmailWithSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_api_send_reset_password_email_with_success(self):
        url = reverse('o55_send_reset_password_email_api_endpoint')
        data = {
            'email_or_username': TEST_USER_EMAIL,
            'tel_or_cell': TEST_USER_TEL_NUM,
        }
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        # Confirm.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @transaction.atomic
    def test_api_send_reset_password_email_with_failure(self):
        url = reverse('o55_send_reset_password_email_api_endpoint')
        data = {
            'email_or_username': "some-bad-email@overfiftyfive.com",
            'tel_or_cell': TEST_USER_TEL_NUM,
        }
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        # Confirm.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
