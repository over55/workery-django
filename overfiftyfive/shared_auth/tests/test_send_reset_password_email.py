# from django.core.management import call_command
# from django_tenants.test.cases import TenantTestCase
# from django_tenants.test.client import TenantClient
# from django.urls import reverse
# from shared_foundation import constants
# from shared_foundation.models.o55_user import O55User
# from shared_foundation.utils import (
#     get_random_string,
#     get_unique_username_from_email
# )
#
#
# TEST_USER_EMAIL = "bart@overfiftyfive.com"
# TEST_USER_USERNAME = "bart@overfiftyfive.com"
# TEST_USER_PASSWORD = "123P@$$w0rd"
# TEST_USER_TEL_NUM = "123 123-1234"
# TEST_USER_TEL_EX_NUM = ""
# TEST_USER_CELL_NUM = "123 123-1234"
#
#
#
# class TestSendResetPasswordEmailManagementCommand(TenantTestCase):
#     """
#     Console:
#     python manage.py test shared_auth.tests.test_send_reset_password_email
#     """
#
#     def setUp(self):
#         super(TestSendResetPasswordEmailManagementCommand, self).setUp()
#         self.c = TenantClient(self.tenant)
#         call_command('setup_fixtures', verbosity=0)
#         call_command(
#            'create_executive_account',
#            TEST_USER_EMAIL,
#            TEST_USER_PASSWORD,
#            "Bart",
#            "Mika",
#            TEST_USER_TEL_NUM,
#            TEST_USER_TEL_EX_NUM,
#            TEST_USER_CELL_NUM,
#            verbosity=0
#         )
#
#     def tearDown(self):
#         del self.client
#
#     def test_command(self):
#         call_command('send_reset_password_email', TEST_USER_EMAIL, verbosity=0)
