from django.core.management import call_command
from django.contrib.auth.password_validation import validate_password
from django.test import override_settings
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.password_validation import *


UPPERCASE_CHARACTER_PASSWORD_VALIDATOR_WITH_SINGLE_CHARS_CONFIG = [{
    'NAME': 'shared_foundation.password_validation.UppercaseCharacterPasswortValidator',
    'OPTIONS': {
       'min_occurrence': 1,
    }
}]

UPPERCASE_CHARACTER_PASSWORD_VALIDATOR_WITH_MULTIPLTE_CHARS_CONFIG = [{
    'NAME': 'shared_foundation.password_validation.UppercaseCharacterPasswortValidator',
    'OPTIONS': {
       'min_occurrence': 5,
    }
}]

SPECIAL_CHARACTER_PASSWORD_VALIDATOR_WITH_SINGLE_CHARS_CONFIG = [{
    'NAME': 'shared_foundation.password_validation.SpecialCharacterPasswortValidator',
    'OPTIONS': {
       'min_occurrence': 1,
    }
}]

SPECIAL_CHARACTER_PASSWORD_VALIDATOR_WITH_MULTIPLTE_CHARS_CONFIG = [{
    'NAME': 'shared_foundation.password_validation.SpecialCharacterPasswortValidator',
    'OPTIONS': {
       'min_occurrence': 5,
    }
}]


class TestPasswordValidation(TenantTestCase):
    """
    Run:
    python manage.py test shared_foundation.tests.test_password_validation
    """

    def setUp(self):
        super(TestPasswordValidation, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.client

    @override_settings(AUTH_PASSWORD_VALIDATORS=UPPERCASE_CHARACTER_PASSWORD_VALIDATOR_WITH_SINGLE_CHARS_CONFIG)
    def test_uppercase_password_valdator_with_single_character_and_failure(self):
        try:
            validate_password('123password')
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertIn("Password must contain at least a single uppercase character.", str(e))

    @override_settings(AUTH_PASSWORD_VALIDATORS=UPPERCASE_CHARACTER_PASSWORD_VALIDATOR_WITH_MULTIPLTE_CHARS_CONFIG)
    def test_uppercase_password_valdator_with_multiple_characters_and_failure(self):
        try:
            validate_password('123Password')
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertIn("Password must contain as least 5 uppercase characters", str(e))

    @override_settings(AUTH_PASSWORD_VALIDATORS=UPPERCASE_CHARACTER_PASSWORD_VALIDATOR_WITH_SINGLE_CHARS_CONFIG)
    def test_uppercase_password_valdator_with_success(self):
        validate_password('123Password')
        self.assertTrue(True)

    @override_settings(AUTH_PASSWORD_VALIDATORS=SPECIAL_CHARACTER_PASSWORD_VALIDATOR_WITH_SINGLE_CHARS_CONFIG)
    def test_special_password_valdator_with_single_character_and_failure(self):
        try:
            validate_password('123password')
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertIn("Password must contain at least a single special character.", str(e))

    @override_settings(AUTH_PASSWORD_VALIDATORS=SPECIAL_CHARACTER_PASSWORD_VALIDATOR_WITH_MULTIPLTE_CHARS_CONFIG)
    def test_special_password_valdator_with_multiple_characters_and_failure(self):
        try:
            validate_password('123Password')
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertIn("Password must contain as least 5 special characters", str(e))

    @override_settings(AUTH_PASSWORD_VALIDATORS=SPECIAL_CHARACTER_PASSWORD_VALIDATOR_WITH_SINGLE_CHARS_CONFIG)
    def test_special_password_valdator_with_success(self):
        validate_password('123password!')
        self.assertTrue(True)
