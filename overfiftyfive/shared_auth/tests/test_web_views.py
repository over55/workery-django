# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework import status
from shared_foundation.models.o55_user import O55User
from shared_foundation.models import SharedMe
from shared_foundation.models import O55User


TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestSharedAuthWebViews(TenantTestCase):
    """
    Class used to test the web views.

    Console:
    python manage.py test shared_auth.tests.test_web_views
    """

    def setUp(self):
        super(TestSharedAuthWebViews, self).setUp()
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
           verbosity=0
        )

    def tearDown(self):
        del self.client
        users = O55User.objects.all()
        for user in users.all():
            user.delete()

    def test_get_index_page(self):
        response = self.c.get(reverse('o55_login_master'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_redirector_master_page(self):
        """TODO: EXPAND!! """
        user = O55User.objects.get()
        token = Token.objects.get(user_id=user.id)
        response = self.c.get(reverse('o55_login_redirector'), HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_send_reset_password_email_master_page(self):
        response = self.c.get(reverse('o55_send_reset_password_email_master'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_reset_password_email_submitted_page(self):
        response = self.c.get(reverse('o55_send_reset_password_email_submitted'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rest_password_master_page_with_success(self):
        me = SharedMe.objects.get(user__email=TEST_USER_EMAIL)
        url = reverse('o55_reset_password_master', args=[me.pr_access_code])
        response = self.c.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rest_password_master_page_with_bad_pr_access_code(self):
        me = SharedMe.objects.get(user__email=TEST_USER_EMAIL)
        url = reverse('o55_reset_password_master', args=['some-bad-pr-access-code'])
        response = self.c.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_rest_password_master_page_with_expired_pr_access_code(self):
        # Get the user profile.
        me = SharedMe.objects.get(user__email=TEST_USER_EMAIL)

        # Set the expiry date to be old!
        today = timezone.now()
        today_minus_1_year = today - timedelta(minutes=1)
        me.pr_expiry_date = today_minus_1_year
        me.save()

        # Run our test...
        url = reverse('o55_reset_password_master', args=[me.pr_access_code])
        response = self.c.get(url)

        # Verify the results.
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_rest_rest_password_detail_page_with_success(self):
        me = SharedMe.objects.get(user__email=TEST_USER_EMAIL)
        url = reverse('o55_reset_password_detail', args=[me.pr_access_code])
        response = self.c.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
