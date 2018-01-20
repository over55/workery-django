# -*- coding: utf-8 -*-
from django.core.management import call_command
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation import constants
from shared_foundation.models.o55_user import O55User


TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestCreateExecutiveAccountManagementCommand(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.commands.test_create_executive_account
    """
    def setUp(self):
        super(TestCreateExecutiveAccountManagementCommand, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)

    def tearDown(self):
        users = O55User.objects.all()
        for user in users.all():
            user.delete()
        del self.c
        super(TestCreateExecutiveAccountManagementCommand, self).tearDown()

    def test_command_with_success(self):
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

        # Verify the account works.
        from django.contrib.auth.hashers import check_password
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.filter(email__iexact=TEST_USER_EMAIL)[0]
        is_authenticated = check_password(TEST_USER_PASSWORD, user.password)
        self.assertTrue(is_authenticated)

    def test_command_with_duplicate_email_error(self):
        O55User.objects.create(
            first_name="Bart",
            last_name="Mika",
            email=TEST_USER_EMAIL,
            username=get_unique_username_from_email(TEST_USER_EMAIL),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        try:
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
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertIn("Email already exists", str(e))
