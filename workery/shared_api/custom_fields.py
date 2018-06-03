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


import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    https://gist.github.com/yprez/7704036
    https://stackoverflow.com/questions/28036404/django-rest-framework-upload-image-the-submitted-data-was-not-a-file#28036805
    """
    def from_native(self, data):
        if isinstance(data, basestring) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super(Base64ImageField, self).from_native(data)
