# -*- coding: utf-8 -*-
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse


class TestHomeViews(TenantTestCase):
    """
    Class used to test the "views".

    Console:
    python manage.py test shared_home.tests.test_views
    """

    def setUp(self):
        super(TestHomeViews, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.c

    def test_get_index_page(self):
        response = self.c.get(reverse('o55_index_master'))
        self.assertEqual(response.status_code, 200)

    def test_http_404_page(self):
        response = self.c.get(reverse('o55_http_404_master'))
        self.assertEqual(response.status_code, 200)

    def test_http_500_page(self):
        response = self.c.get(reverse('o55_http_500_master'))
        self.assertEqual(response.status_code, 200)
