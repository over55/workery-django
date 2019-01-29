# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.db import transaction
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation import constants
from shared_foundation.models import SharedUser


TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestCreateSharedAccountManagementCommand(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.commands.test_create_shared_account
    """
    @transaction.atomic
    def setUp(self):
        super(TestCreateSharedAccountManagementCommand, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)

    @transaction.atomic
    def tearDown(self):
        users = SharedUser.objects.all()
        for user in users.all():
            user.delete()
        del self.c
        super(TestCreateSharedAccountManagementCommand, self).tearDown()

    @transaction.atomic
    def test_command_with_success(self):
        call_command(
           'create_shared_account',
           TEST_USER_EMAIL,
           TEST_USER_PASSWORD,
           "Bart",
           "Mika",
           verbosity=0
        )

        # Verify the account works.
        from django.contrib.auth.hashers import check_password
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.filter(email__iexact=TEST_USER_EMAIL)[0]
        is_authenticated = check_password(TEST_USER_PASSWORD, user.password)
        self.assertTrue(is_authenticated)

    @transaction.atomic
    def test_command_with_duplicate_email_error(self):
        SharedUser.objects.create(
            first_name="Bart",
            last_name="Mika",
            email=TEST_USER_EMAIL,
            is_active=True,
        )
        try:
            call_command(
               'create_shared_account',
               TEST_USER_EMAIL,
               TEST_USER_PASSWORD,
               "Bart",
               "Mika",
               verbosity=0
            )
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertIn("Email already exists", str(e))
