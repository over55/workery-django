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


class APILoginWithPublicSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.test_login_views
    """
    @classmethod
    def setUpTestData(cls):
        pass

    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(APILoginWithPublicSchemaTestCase, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('setup_fixtures', verbosity=0)
        call_command('create_executive_account', TEST_USER_EMAIL, TEST_USER_PASSWORD, "Bart", "Mika", verbosity=0)

    @transaction.atomic
    def tearDown(self):
        users = User.objects.all()
        for user in users.all():
            user.delete()
        super(APILoginWithPublicSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_api_login_with_success(self):
        url = reverse('o55_login_api_endpoint')
        data = {
            'email_or_username': TEST_USER_USERNAME,
            'password': TEST_USER_PASSWORD,
        }
        response = self.c.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['token']) > 0, True)
        self.assertEqual(len(response.data['me']) > 0, True)

    @transaction.atomic
    def test_api_login_with_nonexisting_account(self):
        url = reverse('o55_login_api_endpoint')
        data = {
            'email_or_username': 'hideauze',
            'password': 'Evolvers',
        }
        response = self.c.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def test_api_login_with_inactive_account(self):
        # Get our current user and set the user to be inactive.
        client = User.objects.get()
        client.is_active = False
        client.save()

        # Run this test.
        url = reverse('o55_login_api_endpoint')
        data = {
            'email_or_username': TEST_USER_USERNAME,
            'password': TEST_USER_PASSWORD,
        }
        response = self.c.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def test_api_login_with_bad_password(self):
        # Get our current user and set the user to be inactive.
        client = User.objects.get()
        client.save()

        # Run this test.
        url = reverse('o55_login_api_endpoint')
        data = {
            'email_or_username': TEST_USER_USERNAME,
            'password': "La la la!",
        }
        response = self.c.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
