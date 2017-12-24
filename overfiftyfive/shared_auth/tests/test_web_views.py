from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse


class TestSharedAuthViews(TenantTestCase):
    """
    Class used to test the "views".

    Console:
    python manage.py test shared_auth.tests.test_web_views
    """

    def setUp(self):
        super(TestSharedAuthViews, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.client

    def test_get_index_page(self):
        response = self.c.get(reverse('o55_login_master'))
        self.assertEqual(response.status_code, 200)

    def test_user_login_redirector_master_page(self):
        response = self.c.get(reverse('o55_login_redirector'))
        self.assertEqual(response.status_code, 302)
