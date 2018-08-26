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
from shared_api.serializers.auth_reset_password_serializers import ResetPasswordSerializer


TEST_SCHEMA_NAME = "test"
TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class AuthResetPasswordSerializerWithPublicSchemaTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test shared_api.tests.serializers.test_auth_reset_password_serializers
    """

    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(AuthResetPasswordSerializerWithPublicSchemaTestCase, self).setUp()
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
        super(AuthResetPasswordSerializerWithPublicSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_validate_with_success(self):
        user = SharedUser.objects.get()
        pr_access_code = user.generate_pr_code()
        login_data = {
            'password': TEST_USER_PASSWORD,
            'password_repeat': TEST_USER_PASSWORD,
            'pr_access_code': pr_access_code
        }
        serializer = ResetPasswordSerializer(data=login_data)
        output = serializer.is_valid(raise_exception=True)
        self.assertTrue(output)

    @transaction.atomic
    def test_validate_with_failure(self):
        user = SharedUser.objects.get()
        pr_access_code = user.generate_pr_code()
        login_data = {
            'password': TEST_USER_PASSWORD,
            'password_repeat': TEST_USER_PASSWORD,
            'pr_access_code': 'some-bad-pr-access-code'
        }
        serializer = ResetPasswordSerializer(data=login_data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            self.assertIn("Password reset access code does not exist.", str(e))
