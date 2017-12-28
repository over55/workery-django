# -*- coding: utf-8 -*-
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


class GetIsUniqueWithPublicSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.test_get_is_unique_views
    """
    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(GetIsUniqueWithPublicSchemaTestCase, self).setUp()
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
        super(GetIsUniqueWithPublicSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_anonymous_get_with_200(self):
        # CASE 1 OF 2:
        url = reverse('o55_get_is_unique_api_endpoint')+"?email="+TEST_USER_EMAIL
        response = self.c.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, int(response.content))

        # CASE 2 OF 2:
        url = reverse('o55_get_is_unique_api_endpoint')+"?email=trudy@overfiftyfive.com"
        response = self.c.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, int(response.content))
