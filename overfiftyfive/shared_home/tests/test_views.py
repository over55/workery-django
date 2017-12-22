from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse


class TestHomeViews(TenantTestCase):
    """
    Class used to test the "views".
    """

    def setUp(self):
        super(TestHomeViews, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.client

    def test_get_index_page(self):
        response = self.c.get(reverse('o55_index_master'))
        self.assertEqual(response.status_code, 200)
