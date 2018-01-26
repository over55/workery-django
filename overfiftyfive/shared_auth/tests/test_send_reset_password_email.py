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


class TestSendResetPasswordEmailManagementCommand(TenantTestCase):
    """
    Console:
    python manage.py test shared_auth.tests.test_send_reset_password_email
    """

    def setUp(self):
        super(TestSendResetPasswordEmailManagementCommand, self).setUp()
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

    def tearDown(self):
        del self.c
        users = O55User.objects.all()
        for user in users.all():
            user.delete()
        super(TestSendResetPasswordEmailManagementCommand, self).tearDown()

    def test_command_with_success(self):
        call_command('send_reset_password_email', TEST_USER_EMAIL, verbosity=0)

    def test_command_with_missing_email_error(self):
        try:
            call_command('send_reset_password_email', "trudy@overfiftyfive.com", verbosity=0)
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertIn("Account does not exist with the email or username", str(e))
