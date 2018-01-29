# -*- coding: utf-8 -*-
import json
from django.core.management import call_command
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django.db import connection # Used for django tenants.
from django.db import transaction
from django.db.models import Q
from django.test import TestCase
from django.test import Client
from django.utils import translation
from django.urls import reverse
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from shared_foundation import constants
from shared_foundation.models.o55_user import O55User
from tenant_foundation.models import (
    Associate,
    Customer,
    Order
)


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
python manage.py test tenant_api.tests.test_order_view
"""


class OrderListCreateAPIViewWithTenantTestCase(APITestCase, TenantTestCase):

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
        super(OrderListCreateAPIViewWithTenantTestCase, self).setUp()

        # Load up the dependat.
        call_command('init_app', verbosity=0)
        call_command('populate_tenant_sample_db', TEST_SCHEMA_NAME, verbosity=0)

        # Get objects.
        self.customer = Customer.objects.get(owner__email='sikari@overfiftyfive.com')
        self.associate = Associate.objects.get(owner__email='rayanami@overfiftyfive.com')

        # Get tokens.
        exec_token = Token.objects.get(user__email='bart+executive@overfiftyfive.com')
        manager_token = Token.objects.get(user__email='bart+manager@overfiftyfive.com')
        frontline_token = Token.objects.get(user__email='fherbert@overfiftyfive.com')
        associate_token = Token.objects.get(user__email='rayanami@overfiftyfive.com')
        customer_token = Token.objects.get(user__email='sikari@overfiftyfive.com')

        # Setup.
        self.unauthorized_client = TenantClient(self.tenant)
        self.exec_client = TenantClient(self.tenant, HTTP_AUTHORIZATION='Token ' + exec_token.key)
        self.exec_client.login(
            username='bart+executive@overfiftyfive.com',
            password=TEST_USER_PASSWORD
        )
        self.manager_client = TenantClient(self.tenant, HTTP_AUTHORIZATION='Token ' + manager_token.key)
        self.manager_client.login(
            username='bart+manager@overfiftyfive.com',
            password=TEST_USER_PASSWORD
        )
        self.staff_client = TenantClient(self.tenant, HTTP_AUTHORIZATION='Token ' + manager_token.key)
        self.staff_client.login(
            username='fherbert@overfiftyfive.com',
            password=TEST_USER_PASSWORD
        )
        self.customer_client = TenantClient(self.tenant, HTTP_AUTHORIZATION='Token ' + manager_token.key)
        self.customer_client.login(
            username='rayanami@overfiftyfive.com',
            password=TEST_USER_PASSWORD
        )

        # Load up the tenant.
        connection.set_schema(TEST_SCHEMA_NAME, True) # Switch to Tenant.

        # Create our order.
        self.order = Order.objects.create(
            customer=Customer.objects.get(owner__email="sikari@overfiftyfive.com"),
            associate=Associate.objects.get(owner__email="rayanami@overfiftyfive.com"),
            assignment_date=timezone.now(),
            created_by=O55User.objects.get(email="fherbert@overfiftyfive.com"),
            last_modified_by=None
        )

    @transaction.atomic
    def tearDown(self):
        connection.set_schema(TEST_SCHEMA_NAME, True) # Switch to Tenant.
        Order.objects.delete_all()
        del self.unauthorized_client
        del self.exec_client
        del self.manager_client
        del self.staff_client
        del self.customer_client
        super(OrderListCreateAPIViewWithTenantTestCase, self).tearDown()

    #-------------------#
    # List API-endpoint #
    #-------------------#

    @transaction.atomic
    def test_list_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a GET request to the LIST API-endpoint.
        """
        url = reverse('o55_order_list_create_api_endpoint')+"?format=json"
        response = self.unauthorized_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_list_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        GET request to the list API-endpoint.
        """
        url = reverse('o55_order_list_create_api_endpoint')
        url += "?format=json"

        # Executive
        response = self.exec_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Manager
        response = self.manager_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Staff
        response = self.staff_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @transaction.atomic
    def test_list_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a GET request to the list API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_order_list_create_api_endpoint')
        url += "?format=json"
        response = self.customer_client.get(url, data=None, content_type='application/json')
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
        url = reverse('o55_order_list_create_api_endpoint')+"?format=json"
        response = self.unauthorized_client.post(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_create_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        POST request to the create API-endpoint.
        """
        url = reverse('o55_order_list_create_api_endpoint')
        url += "?format=json"

        # Executive
        response = self.exec_client.post(url, data=json.dumps({
            'customer': self.customer.id,
            'associate': self.associate.id,
            'given_name': 'Bart',
            'middle_name': '',
            'last_name': 'Mika',
            'address_country': 'CA',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'street_address': '78 Riverside Drive',
            'postal_code': 'N6H 1B4',
            'assignment_date': "2018-01-30",
            'category_tags': [],
            'comments': []
        }), content_type='application/json')
        self.assertIsNotNone(response)
        # print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Shinji", str(response.data))
        self.assertIn("Ikari", str(response.data))
        self.assertIn("Rei", str(response.data))
        self.assertIn("Ayanami", str(response.data))

        # Manager
        response = self.manager_client.post(url, data=json.dumps({
            'customer': self.customer.id,
            'associate': self.associate.id,
            'given_name': 'Bart',
            'middle_name': '',
            'last_name': 'Mika',
            'address_country': 'CA',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'street_address': '78 Riverside Drive',
            'postal_code': 'N6H 1B4',
            'assignment_date': "2018-01-30",
            'category_tags': [],
            'comments': []
        }), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Shinji", str(response.data))
        self.assertIn("Ikari", str(response.data))
        self.assertIn("Rei", str(response.data))
        self.assertIn("Ayanami", str(response.data))

        # Staff
        response = self.staff_client.post(url, data=json.dumps({
            'customer': self.customer.id,
            'associate': self.associate.id,
            'given_name': 'Bart',
            'middle_name': '',
            'last_name': 'Mika',
            'address_country': 'CA',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'street_address': '78 Riverside Drive',
            'postal_code': 'N6H 1B4',
            'assignment_date': "2018-01-30",
            'category_tags': [],
            'comments': []
        }), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Shinji", str(response.data))
        self.assertIn("Ikari", str(response.data))
        self.assertIn("Rei", str(response.data))
        self.assertIn("Ayanami", str(response.data))

    @transaction.atomic
    def test_create_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a POST request to the list API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_order_list_create_api_endpoint')
        url += "?format=json"
        response = self.customer_client.post(url, data=json.dumps({}), content_type='application/json')
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
        url = reverse('o55_order_retrieve_update_destroy_api_endpoint', args=[self.order.id])+"?format=json"
        response = self.unauthorized_client.post(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_update_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        PUT request to the update API-endpoint.
        """
        url = reverse('o55_order_retrieve_update_destroy_api_endpoint', args=[self.order.id])+"?format=json"
        data = json.dumps({
            'customer': self.customer.id,
            'associate': self.associate.id,
            'completion_date': '2019-01-25',
            'assignment_date': "2018-01-30",
            'category_tags': [],
            'comments': []
        })

        # Executive
        response = self.exec_client.put(url, data=data, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("2019-01-25", str(response.data))
        self.assertIn("2018-01-30", str(response.data))

        # Manager
        response = self.manager_client.put(url, data=data, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("2019-01-25", str(response.data))
        self.assertIn("2018-01-30", str(response.data))

        # Staff
        response = self.staff_client.put(url, data=data, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("2019-01-25", str(response.data))
        self.assertIn("2018-01-30", str(response.data))

    @transaction.atomic
    def test_update_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a PUT request to the update API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_order_retrieve_update_destroy_api_endpoint', args=[self.order.id])+"?format=json"
        data = json.dumps({
            'customer': self.customer.id,
            'associate': self.associate.id,
            'completion_date': '2019-01-25',
            'assignment_date': "2018-01-30",
            'category_tags': [],
            'comments': []
        })
        response = self.customer_client.put(url, data=data, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))

    #-----------------------#
    # Retrieve API-endpoint #
    #-----------------------#

    @transaction.atomic
    def test_retrieve_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a GET request to the retrieve API-endpoint.
        """
        url = reverse('o55_order_retrieve_update_destroy_api_endpoint', args=[self.order.id])+"?format=json"
        response = self.unauthorized_client.get(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_retrieve_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        GET request to the retrieve API-endpoint.
        """
        url = reverse('o55_order_retrieve_update_destroy_api_endpoint', args=[self.order.id])+"?format=json"

        response = self.exec_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Rei", str(response.data))
        self.assertIn("Shinji", str(response.data))

        response = self.manager_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Rei", str(response.data))
        self.assertIn("Shinji", str(response.data))

        response = self.staff_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Rei", str(response.data))
        self.assertIn("Shinji", str(response.data))

    @transaction.atomic
    def test_retrieve_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a GET request to the retrieve API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_order_retrieve_update_destroy_api_endpoint', args=[self.order.id])+"?format=json"
        response = self.exec_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))

    #-----------------------#
    # Delete API-endpoint #
    #-----------------------#

    @transaction.atomic
    def test_delete_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a DELETE request to the delete API-endpoint.
        """
        url = reverse('o55_order_retrieve_update_destroy_api_endpoint', args=[self.order.id])+"?format=json"
        response = self.unauthorized_client.delete(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_delete_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        DELETE request to the delete API-endpoint.
        """
        url = reverse('o55_order_retrieve_update_destroy_api_endpoint', args=[self.order.id])+"?format=json"
        response = self.exec_client.delete(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @transaction.atomic
    def test_delete_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a DELETE request to the delete API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('o55_order_retrieve_update_destroy_api_endpoint', args=[self.order.id])+"?format=json"
        response = self.exec_client.delete(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))
