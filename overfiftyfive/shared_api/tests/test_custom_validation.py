from django.core.management import call_command
from django.db.models import Q
from django.db import transaction
from django.test import TestCase
from django.test import Client
from django.utils import translation
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import serializers
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from shared_api.custom_validation import *
from shared_foundation import constants


"""
Console:
python manage.py test shared_api.tests.test_custom_validation
"""


# - - - - - - - - - - - - - - - -
# MatchingDuelFieldsValidator
# - - - - - - - - - - - - - - - -


class MatchingDuelFieldsValidatorSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=63,
        style={'input_type': 'password'},
        validators = [
            MatchingDuelFieldsValidator(
                another_field='password_repeat',
                message="Inputted passwords fields do not match."
            )
        ]
    )
    password_repeat = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=63,
        style={'input_type': 'password'}
    )


class TestMatchingDuelFieldsValidatorWithPublicSchemaTestCase(APITestCase, TenantTestCase):
    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(TestMatchingDuelFieldsValidatorWithPublicSchemaTestCase, self).setUp()
        self.c = TenantClient(self.tenant)

    @transaction.atomic
    def tearDown(self):
        users = User.objects.all()
        for user in users.all():
            user.delete()
        super(TestMatchingDuelFieldsValidatorWithPublicSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_validation(self):
        # CASE 1 OF 2: Failure
        data = {
            'password': 'some-bad-email@overfiftyfive.com',
            'password_repeat': '123 123-1234'
        }
        s = MatchingDuelFieldsValidatorSerializer(data=data)

        try:
            s.is_valid(raise_exception=True)
        except Exception as e:
            self.assertIn("Inputted passwords fields do not match", str(e))

        # CASE 2 OF 2: Success
        data = {
            'password': 'some-matching-password',
            'password_repeat': 'some-matching-password'
        }
        s = MatchingDuelFieldsValidatorSerializer(data=data)
        result = s.is_valid(raise_exception=False)
        self.assertTrue(result)


# - - - - - - - - - - - - - - - - - - - - -
# EnhancedPasswordStrengthFieldValidator
# - - - - - - - - - - - - - - - - - - - - -


class EnhancedPasswordStrengthFieldValidatorSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=63,
        style={'input_type': 'password'},
        validators = [
            EnhancedPasswordStrengthFieldValidator()
        ]
    )


class TestEnhancedPasswordStrengthFieldValidatorWithPublicSchemaTestCase(APITestCase, TenantTestCase):
    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(TestEnhancedPasswordStrengthFieldValidatorWithPublicSchemaTestCase, self).setUp()
        self.c = TenantClient(self.tenant)

    @transaction.atomic
    def tearDown(self):
        users = User.objects.all()
        for user in users.all():
            user.delete()
        super(TestEnhancedPasswordStrengthFieldValidatorWithPublicSchemaTestCase, self).tearDown()

    @transaction.atomic
    def test_validation(self):
        # CASE 1 OF 2: Failure
        data = {'password': 'some-bad-password',}
        s = EnhancedPasswordStrengthFieldValidatorSerializer(data=data)
        result = s.is_valid(raise_exception=False)
        self.assertFalse(result)

        # CASE 2 OF 2: Success
        data = {'password': 'qm9pQs6X8cxRxjtvuh4Licd8tLufq8AWqzS4TkA5C6fcASGS$',}
        s = EnhancedPasswordStrengthFieldValidatorSerializer(data=data)
        result = s.is_valid(raise_exception=False)
        self.assertTrue(result)


# - - - - - - - - - - - - - - -
# OnlyTrueBooleanFieldValidator
# - - - - - - - - - - - - - - -

#TODO: IMP
