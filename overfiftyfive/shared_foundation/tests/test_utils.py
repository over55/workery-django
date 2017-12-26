from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.conf import settings
from django.urls import reverse
from shared_foundation.utils import *


class TestUtils(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.test_utils
    """

    def setUp(self):
        super(TestUtils, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.c

    def test_reverse_with_full_domain(self):
        value = reverse_with_full_domain("o55_index_master")
        self.assertIsNotNone(value)
        self.assertIn(settings.O55_APP_HTTP_PROTOCOL+settings.O55_APP_HTTP_DOMAIN+"/en/", value)
