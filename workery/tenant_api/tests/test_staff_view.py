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
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate, login, logout
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from shared_foundation import constants
from shared_foundation.utils import get_jwt_token_and_orig_iat
from shared_foundation.models import SharedUser
from tenant_foundation.models import (
    Staff,
    SkillSet
)


TEST_SCHEMA_NAME = "london"
TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"
TEST_ALERNATE_USER_EMAIL = "rodolfo@workery.ca"


class StaffListCreateAPIViewWithTenantTestCase(APITestCase, TenantTestCase):
    """
    Console:
    python manage.py test tenant_api.tests.test_staff_view
    """

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
        super(StaffListCreateAPIViewWithTenantTestCase, self).setUp()

        # Load up the dependat.
        call_command('init_app', verbosity=0)
        call_command('populate_tenant_content', TEST_SCHEMA_NAME, verbosity=0)

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
           "Rodolfo",
           "Martinez",
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
        self.user = SharedUser.objects.get(email=TEST_USER_EMAIL)
        self.alternate_user = SharedUser.objects.get(email=TEST_ALERNATE_USER_EMAIL)
        token, orig_iat = get_jwt_token_and_orig_iat(self.user)

        # Setup.
        self.unauthorized_client = TenantClient(self.tenant)
        self.authorized_client = TenantClient(self.tenant, HTTP_AUTHORIZATION='JWT {0}'.format(token))
        self.authorized_client.login(
            username=TEST_USER_USERNAME,
            password=TEST_USER_PASSWORD
        )
        # Create our staff.
        connection.set_schema(TEST_SCHEMA_NAME, True) # Switch to Tenant.
        self.staff = Staff.objects.create(
            owner=self.user,
            given_name="Bart",
            last_name="Mika"
        )
        self.alernate_staff = Staff.objects.create(
            owner=self.alternate_user,
            given_name="Rodolfo",
            last_name="Martinez"
        )

    @transaction.atomic
    def tearDown(self):
        connection.set_schema(TEST_SCHEMA_NAME, True) # Switch to Tenant.
        Staff.objects.delete_all()
        del self.unauthorized_client
        del self.authorized_client
        super(StaffListCreateAPIViewWithTenantTestCase, self).tearDown()

    #-------------------#
    # List API-endpoint #
    #-------------------#

    @transaction.atomic
    def test_list_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a GET request to the LIST API-endpoint.
        """
        url = reverse('workery_staff_list_create_api_endpoint')+"?format=json"
        response = self.unauthorized_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_list_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        GET request to the list API-endpoint.
        """
        url = reverse('workery_staff_list_create_api_endpoint')
        url += "?format=json"
        response = self.authorized_client.get(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Bart", str(response.data))
        self.assertIn("Mika", str(response.data))
        self.assertNotIn("You do not have permission to access this API-endpoint.", str(response.data))

    @transaction.atomic
    def test_list_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a GET request to the list API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('workery_staff_list_create_api_endpoint')
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
        url = reverse('workery_staff_list_create_api_endpoint')+"?format=json"
        response = self.unauthorized_client.post(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_create_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        POST request to the create API-endpoint.
        """
        # Perform our tests.
        url = reverse('workery_staff_list_create_api_endpoint')
        url += "?format=json"
        response = self.authorized_client.post(url, data=json.dumps({
            'password': '123Password!',
            'password_repeat': '123Password!',
            'groups': [
                constants.MANAGEMENT_GROUP_ID
            ],
            'email': "bart+staff@workery.ca",
            'given_name': 'Bart',
            'middle_name': '',
            'last_name': 'Mika',
            'address_country': 'CA',
            'address_locality': 'London',
            'address_region': 'Ontario',
            'street_address': '78 Riverside Drive',
            'postal_code': 'N6H 1B4',
            'telephone': '(123) 456-7890',
            'telephone_extension': None,
            'fax_number': None,
            'other_telephone': '+19876543210',
            'extra_comment': "This is a friendly staff.",
            'group_membership': 2,
            'is_active': True,
            'password': '123passwordOK!',
            'password_repeat': '123passwordOK!',
            'description': 'Some generic desc.',
            'telephone_type_of': 1,
            'other_telephone_type_of': 1,
            'is_ok_to_email': True,
            'is_ok_to_text': True,
            'tags': [],
            'account_type': constants.FRONTLINE_GROUP_ID
        }), content_type='application/json')
        self.assertIsNotNone(response)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Bart", str(response.data))
        self.assertIn("Mika", str(response.data))
        self.assertIn("(123) 456-7890", str(response.data))
        self.assertIn("(987) 654-3210", str(response.data))

    @transaction.atomic
    def test_create_with_403_by_permissions(self):
        """
        Unit test will test authenticated user, who does not have permission, to
        make a POST request to the list API-endpoint.
        """
        Permission.objects.all().delete()
        url = reverse('workery_staff_list_create_api_endpoint')
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
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.staff.id])+"?format=json"
        response = self.unauthorized_client.post(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_update_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        PUT request to the update API-endpoint.
        """
         # Perform our tests.
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.alernate_staff.id])+"?format=json"
        response = self.authorized_client.put(url, data=json.dumps({
            # 'email': TEST_ALERNATE_USER_EMAIL,
            'given_name': 'Rodolfo',
            'middle_name': '',
            'last_name': 'Martinez',
            'address_country': 'CA',
            'address_locality': 'Port Frank Herbert',
            'address_region': 'Britich Coloumbia',
            'street_address': '666 Riverside Drive',
            'postal_code': 'N1N 1N1',
            'extra_comment': "This is a helpful staff.",
            'group_membership': 2,
            'is_active': True,
            'password': '123passwordOK!',
            'password_repeat': '123passwordOK!',
            'description': 'Some generic desc.',
            'telephone_type_of': 1,
            'other_telephone_type_of': 1,
            'is_ok_to_email': True,
            'is_ok_to_text': True,
            'tags': [],
            'account_type': constants.FRONTLINE_GROUP_ID
        }), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Rodolfo", str(response.data))
        self.assertIn("Martinez", str(response.data))
        self.assertIn("666 Riverside Drive", str(response.data))
        self.assertIn("N1N 1N1", str(response.data))
        self.assertIn("Port Frank Herbert", str(response.data))

    # # @transaction.atomic
    # # def test_update_with_403_by_permissions(self):
    # #     """
    # #     Unit test will test authenticated user, who does not have permission, to
    # #     make a PUT request to the update API-endpoint.
    # #     """
    # #     Permission.objects.all().delete()
    # #     url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.alernate_staff.id])+"?format=json"
    # #     response = self.authorized_client.put(url, data=json.dumps({}), content_type='application/json')
    # #     self.assertIsNotNone(response)
    # #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    # #     self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))

    @transaction.atomic
    def test_update_with_200_by_ownership(self):
        # Perform our tests.
        Permission.objects.all().delete()
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.staff.id])+"?format=json"
        response = self.authorized_client.put(url, data=json.dumps({
            # 'email': 'bart@workery.ca',
            'given_name': 'Bartlomiej',
            'middle_name': '',
            'last_name': 'Mika',
            'address_country': 'CA',
            'address_locality': 'Port Bart',
            'address_region': 'Alberta',
            'street_address': '666 Riverside Drive',
            'postal_code': 'N1N 1N1',
            # 'extra_comment': "This is a helpful staff.",
            'group_membership': 2,
            'is_active': True,
            'password': '123passwordOK!',
            'password_repeat': '123passwordOK!',
            'description': 'Some generic desc.',
            'telephone_type_of': 1,
            'other_telephone_type_of': 1,
            'is_ok_to_email': True,
            'is_ok_to_text': True,
            'tags': [],
            'account_type': constants.FRONTLINE_GROUP_ID
        }), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Bartlomiej", str(response.data))
        self.assertIn("Mika", str(response.data))
        self.assertIn("666 Riverside Drive", str(response.data))
        self.assertIn("N1N 1N1", str(response.data))
        self.assertIn("Port Bart", str(response.data))

    @transaction.atomic
    def test_update_with_200_by_ownership_and_password_change(self):
        # Perform our tests.
        Permission.objects.all().delete()
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.staff.id])+"?format=json"
        response = self.authorized_client.put(url, data=json.dumps({
            'password': '123Password!',
            'password_repeat': '123Password!',
            # 'email': 'bart@workery.ca',
            'given_name': 'Bartlomiej',
            'middle_name': '',
            'last_name': 'Mika',
            'address_country': 'CA',
            'address_locality': 'Port Bart',
            'address_region': 'Alberta',
            'street_address': '666 Riverside Drive',
            'postal_code': 'N1N 1N1',
            # 'extra_comment': "This is a helpful staff.",
            'group_membership': 2,
            'is_active': True,
            'password': '123passwordOK!',
            'password_repeat': '123passwordOK!',
            'description': 'Some generic desc.',
            'telephone_type_of': 1,
            'other_telephone_type_of': 1,
            'is_ok_to_email': True,
            'is_ok_to_text': True,
            'tags': [],
            'account_type': constants.FRONTLINE_GROUP_ID
        }), content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Bartlomiej", str(response.data))
        self.assertIn("Mika", str(response.data))
        self.assertIn("666 Riverside Drive", str(response.data))
        self.assertIn("N1N 1N1", str(response.data))
        self.assertIn("Port Bart", str(response.data))

    #-----------------------#
    # Retrieve API-endpoint #
    #-----------------------#

    @transaction.atomic
    def test_retrieve_with_401_by_permissions(self):
        """
        Unit test will test anonymous make a GET request to the retrieve API-endpoint.
        """
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.staff.id])+"?format=json"
        response = self.unauthorized_client.get(url, data={}, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @transaction.atomic
    def test_retrieve_with_200_by_permissions(self):
        """
        Unit test will test authenticated user, who has permission, to make a
        GET request to the retrieve API-endpoint.
        """
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.staff.id])+"?format=json"
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
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.alernate_staff.id])+"?format=json"
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
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.staff.id])+"?format=json"
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
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.staff.id])+"?format=json"
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
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.staff.id])+"?format=json"
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
        url = reverse('workery_staff_retrieve_update_destroy_api_endpoint', args=[self.staff.id])+"?format=json"
        response = self.authorized_client.delete(url, data=None, content_type='application/json')
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission to access this API-endpoint.", str(response.data))
