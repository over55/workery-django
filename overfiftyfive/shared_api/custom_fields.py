import phonenumbers
from rest_framework import serializers


class PhoneNumberField(serializers.Field):
    """
    Class used to convert the "PhoneNumber" objects "to" and "from" strings.
    This objects is from the "python-phonenumbers" library.
    """
    def to_representation(self, obj):
        """
        Function used to convert the PhoneNumber object to text string
        representation.
        """
        try:
            return phonenumbers.format_number(obj, phonenumbers.PhoneNumberFormat.NATIONAL)
        except Exception as e:
            return None

    def to_internal_value(self, text):
        """
        Function used to conver the text into the PhoneNumber object
        representation.
        """
        try:
            obj = phonenumbers.parse(text, "CA")
            return phonenumbers.format_number(obj, phonenumbers.PhoneNumberFormat.NATIONAL)
        except Exception as e:
            return None

# python-phonenumbers - https://github.com/daviddrysdale/python-phonenumbers
# Custom Fields - http://www.django-rest-framework.org/api-guide/fields/#custom-fields
