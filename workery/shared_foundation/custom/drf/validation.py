import re
from rest_framework import exceptions, serializers
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _


class MatchingDuelFieldsValidator(object):
    """
    Validator ensures two different fields in a serializer have similar strings.
    """
    def __init__(self, another_field, message):
        self.another_field = another_field
        self.message = message

    def set_context(self, serializer_field):
        self.serializer_field = serializer_field

    def __call__(self, value):
        serializer = self.serializer_field.parent
        raw_string_repeat = serializer.initial_data[self.another_field]

        if value != raw_string_repeat:
            raise serializers.ValidationError(self.message)


class EnhancedPasswordStrengthFieldValidator(object):
    """
    Validator ensures passwords are "high-quality".
    """
    def __init__(self):
        pass

    def __call__(self, value):
        validate_password(value)


class OnlyTrueBooleanFieldValidator(object):
    """
    Validator ensures a django-rest-serializer "BooleanField" value is only
    set as "True".
    """
    def __init__(self, message):
        self.message = message

    def __call__(self, value):
        if value is False:
            raise serializers.ValidationError(self.message)
