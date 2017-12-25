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
        self.assertEqual(response.status_code, 200)

    def test_user_login_redirector_master_page(self):
        response = self.c.get(reverse('o55_login_redirector'))
        self.assertEqual(response.status_code, 302)

    def test_send_reset_password_email_master_page(self):
        response = self.c.get(reverse('o55_send_reset_password_email_master'))
        self.assertEqual(response.status_code, 200)

    def test_send_reset_password_email_submitted_page(self):
        response = self.c.get(reverse('o55_send_reset_password_email_submitted'))
        self.assertEqual(response.status_code, 200)

    def test_rest_password_master_page_with_success(self):
        me = SharedMe.objects.get(user__email=TEST_USER_EMAIL)
        url = reverse('o55_reset_password_master', args=[me.pr_access_code])
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)
