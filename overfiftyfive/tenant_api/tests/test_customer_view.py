# -*- coding: utf-8 -*-
import json
from django.core.management import call_command
from django.db import connection # Used for django tenants.
from django.db import transaction
from django.db.models import Q
from django.test import TestCase
from django.test import Client
from django.utils import translation
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from shared_foundation import constants
from tenant_foundation.models import Customer


TEST_SCHEMA_NAME = "london"
TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"
TEST_ALERNATE_USER_EMAIL = "rodolfo@overfiftyfive.com"


"""
Console:
python manage.py test tenant_api.tests.test_customer_view
"""


class CustomerListCreateAPIViewWithTenantTestCase(APITestCase, TenantTestCase):

    #------------------#
    # Setup Unit Tests #
    #------------------#

    def setup_tenant(tenant):
        """Tenant Schema"""
        tenant.schema_name = TEST_SCHEMA_NAME
        tenant.name='Over 55 (London) Inc.',
        tenant.alternate_name="Over55",
        tenant.description="Located at the Forks of the Thames in ...",
        tenant.address_country="CA",
        tenant.address_locality="London",
        tenant.address_region="Ontario",
        tenant.post_office_box_number="", # Post Offic #
        tenant.postal_code="N6H 1B4",
        tenant.street_address="78 Riverside Drive",
        tenant.street_address_extra="", # Extra line.

    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(CustomerListCreateAPIViewWithTenantTestCase, self).setUp()

        # Load up the dependat.
        call_command('init_app', verbosity=0)

        # Create the account.
        call_command(
           'create_tenant_account',
           TEST_SCHEMA_NAME,
           constants.MANAGEMENT_GROUP_ID,
           TEST_USER_EMAIL,
           TEST_USER_PASSWORD,
           "Bart",
           "Mika",
           TEST_USER_TEL_NUM,
           TEST_USER_TEL_EX_NUM,
           TEST_USER_CELL_NUM,
           "CA",
           "London",
           "Ontario",
           "", # Post Offic #
           "N6H 1B4",
           "78 Riverside Drive",
           "", # Extra line.
           verbosity=0
        )

        # Create the account.
        call_command(
           'create_tenant_account',
           TEST_SCHEMA_NAME,
           constants.MANAGEMENT_GROUP_ID,
           TEST_ALERNATE_USER_EMAIL,
           TEST_USER_PASSWORD,
           "Bart",
           "Mika",
           TEST_USER_TEL_NUM,
           TEST_USER_TEL_EX_NUM,
           TEST_USER_CELL_NUM,
           "CA",
           "London",
           "Ontario",
           "", # Post Offic #
           "N6H 1B4",
           "78 Riverside Drive",
           "", # Extra line.
           verbosity=0
        )

        # Initialize our test data.
        self.user = User.objects.get(email=TEST_USER_EMAIL)
        token = Token.objects.get(user=self.user)

        # Setup.
        self.unauthorized_client = TenantClient(self.tenant)
        self.authorized_client = TenantClient(self.tenant, HTTP_AUTHORIZATION='Token ' + token.key)
        self.authorized_client.login(
            username=TEST_USER_USERNAME,
            password=TEST_USER_PASSWORD
        )
        # Create our customer.
        connection.set_schema(TEST_SCHEMA_NAME, True) # Switch to Tenant.
        self.customer = Customer.objects.create(
            owner=self.user,
            given_name="Bart",
            last_name="Mika"
        )
        self.alernate_customer = Customer.objects.create(
            owner=User.objects.get(email=TEST_ALERNATE_USER_EMAIL),
            given_name="Rodolfo",
            last_name="Martinez"
        )

    @transaction.atomic
    def tearDown(self):
        connection.set_schema(TEST_SCHEMA_NAME, True) # Switch to Tenant.
        Customer.objects.delete_all()
        del self.unauthorized_client
        del self.authorized_client
        super(CustomerListCreateAPIViewWithTenantTestCase, self).tearDown()

    #-------------------#
    # List API-endpoint #
    #-------------------#

    @transaction.atomic
    def test_list_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a GET request to the LIST API-endpoint.
        """
        url = reverse('o55_customer_list_create_api_endpoint')+"?format=json"
        response = self.unauthorized_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_list_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        GET request to the list API-endpoint.
        """
        url = reverse('o55_customer_list_create_api_endpoint')
        url += "?format=json"
        response = self.authorized_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Bart", str(response.data))
        self.assertIn("Mika", str(response.data))

    @transaction.atomic
    def test_list_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a GET request to the list API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_customer_list_create_api_endpoint')
        url += "?format=json"
        response = self.authorized_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))

    #---------------------#
    # Create API-endpoint #
    #---------------------#

    @transaction.atomic
    def test_create_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a POST request to the create API-endpoint.
        """
        url = reverse('o55_customer_list_create_api_endpoint')+"?format=json"
        response = self.unauthorized_client.post(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_create_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        POST request to the create API-endpoint.
        """
        url = reverse('o55_customer_list_create_api_endpoint')
        url += "?format=json"
        response = self.authorized_client.post(url, data=json.dumps({
            'given_name': 'Bart',
            'middle_name': '',
            'last_name': 'Mika',
            'address_country': 'CA',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'street_address': '78 Riverside Drive',
            'postal_code': 'N6H 1B4'
        }), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Bart", str(response.data))
        self.assertIn("Mika", str(response.data))

    @transaction.atomic
    def test_create_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a POST request to the list API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_customer_list_create_api_endpoint')
        url += "?format=json"
        response = self.authorized_client.post(url, data=json.dumps({}), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))

    #---------------------#
    # Update API-endpoint #
    #---------------------#

    @transaction.atomic
    def test_update_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a PUT request to the update API-endpoint.
        """
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.customer.id])+"?format=json"
        response = self.unauthorized_client.post(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_update_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        PUT request to the update API-endpoint.
        """
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.customer.id])+"?format=json"
        response = self.authorized_client.put(url, data=json.dumps({
            'given_name': 'Bartlomiej',
            'middle_name': '',
            'last_name': 'Mika',
            'address_country': 'CA',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'street_address': '78 Riverside Drive',
            'postal_code': 'N6H 1B4'
        }), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Bartlomiej", str(response.data))
        self.assertIn("Mika", str(response.data))

    @transaction.atomic
    def test_update_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a PUT request to the update API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.alernate_customer.id])+"?format=json"
        response = self.authorized_client.put(url, data=json.dumps({}), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))

    @transaction.atomic
    def test_update_with_200_by_ownership(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a PUT request to the update API-endpoint but has ownership of the
        object.
        """
        Permission.objects.all().delete()
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.customer.id])+"?format=json"
        response = self.authorized_client.put(url, data=json.dumps({
            'given_name': 'Bartlomiej',
            'middle_name': '',
            'last_name': 'Mika',
            'address_country': 'CA',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'street_address': '78 Riverside Drive',
            'postal_code': 'N6H 1B4'
        }), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Bartlomiej", str(response.data))
        self.assertIn("Mika", str(response.data))

    #-----------------------#
    # Retrieve API-endpoint #
    #-----------------------#

    @transaction.atomic
    def test_retrieve_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a GET request to the retrieve API-endpoint.
        """
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.customer.id])+"?format=json"
        response = self.unauthorized_client.get(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_retrieve_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        GET request to the retrieve API-endpoint.
        """
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.customer.id])+"?format=json"
        response = self.authorized_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Bart", str(response.data))
        self.assertIn("Mika", str(response.data))

    @transaction.atomic
    def test_retrieve_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a GET request to the retrieve API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.alernate_customer.id])+"?format=json"
        response = self.authorized_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))

    @transaction.atomic
    def test_retrieve_with_200_by_ownership(self):
        """
        Unit test will test authenticated user, who does not have permission,
        but is the OWNER of the object to make a GET request to the retrieve
        API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.customer.id])+"?format=json"
        response = self.authorized_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Bart", str(response.data))
        self.assertIn("Mika", str(response.data))

    #-----------------------#
    # Delete API-endpoint #
    #-----------------------#

    @transaction.atomic
    def test_delete_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a DELETE request to the delete API-endpoint.
        """
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.customer.id])+"?format=json"
        response = self.unauthorized_client.delete(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_delete_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        DELETE request to the delete API-endpoint.
        """
        # Add executive group so you can delete.
        self.user.groups.add(constants.EXECUTIVE_GROUP_ID)

        # Go ahead and delete.
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.customer.id])+"?format=json"
        response = self.authorized_client.delete(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @transaction.atomic
    def test_delete_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a DELETE request to the delete API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_customer_retrieve_update_destroy_api_endpoint', args=[self.customer.id])+"?format=json"
        response = self.authorized_client.delete(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))
