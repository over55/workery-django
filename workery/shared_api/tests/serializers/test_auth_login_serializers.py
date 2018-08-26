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
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError

from shared_foundation import constants
from shared_foundation.models import SharedUser
from shared_api.serializers.auth_login_serializers import AuthCustomTokenSerializer


TEST_SCHEMA_NAME = "test"
TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class AuthLoginSerializerWithPublicSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.serializers.test_auth_login_serializers
    """

    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(AuthLoginSerializerWithPublicSchemaTestCase, self).setUp()
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
        # users = SharedUser.objects.all() #TODO: WHY ERROR WHEN USING THIS?
        users = SharedUser.objects.all()
        for user in users.all():
            user.delete()
        del self.c
        super(AuthLoginSerializerWithPublicSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_validate_with_success(self):
        login_data = {
            'email_or_username': TEST_USER_USERNAME,
            'password': TEST_USER_PASSWORD
        }
        serializer = AuthCustomTokenSerializer(data=login_data)
        serializer.is_valid(raise_exception=True)
        authenticated_user = serializer.validated_data['authenticated_user']
        self.assertIsNotNone(authenticated_user)

    @transaction.atomic
    def test_validate_with_no_email(self):
        login_data = {
            'email_or_username': 'trudy@workery.ca',
            'password': TEST_USER_PASSWORD
        }
        serializer = AuthCustomTokenSerializer(data=login_data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            self.assertIn("This E-Mail address is not registered.", str(e))

    @transaction.atomic
    def test_validate_with_incorrect_password(self):
        login_data = {
            'email_or_username': TEST_USER_USERNAME,
            'password': 'Bad password'
        }
        serializer = AuthCustomTokenSerializer(data=login_data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            self.assertIn("Incorrect Pasword", str(e))

    @transaction.atomic
    def test_validate_with_suspended_account(self):
        login_data = {
            'email_or_username': TEST_USER_USERNAME,
            'password': TEST_USER_PASSWORD
        }
        user = SharedUser.objects.get()
        user.is_active = False
        user.save()
        serializer = AuthCustomTokenSerializer(data=login_data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            self.assertIn("Your account is suspended!", str(e))
