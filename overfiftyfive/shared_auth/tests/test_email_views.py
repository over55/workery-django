# -*- coding: utf-8 -*-
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.models.o55_user import O55User
from shared_foundation.models import SharedMe


TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestSharedAuthEmailViews(TenantTestCase):
    """
    Class used to test the email views.

    Console:
    python manage.py test shared_auth.tests.test_email_views
    """

    def setUp(self):
        super(TestSharedAuthEmailViews, self).setUp()
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
        super(TestSharedAuthEmailViews, self).tearDown()

    def test_reset_password_email_page_with_success(self):
        me = SharedMe.objects.get(user__email=TEST_USER_EMAIL)
        url = reverse('o55_reset_password_email', args=[me.pr_access_code])
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)
