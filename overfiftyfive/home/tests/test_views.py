from django.test import TestCase
from django.test import Client
from django.urls import reverse


class TestHomeViews(TestCase):
    """
    Class used to test the "views".
    """

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        del self.client

    def test_get_index_page(self):
        response = self.client.get(reverse('o55_index_master'))
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
